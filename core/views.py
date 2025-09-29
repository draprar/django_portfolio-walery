from django.views import View
from django.http import JsonResponse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.shortcuts import render
import logging
from .forms import ContactForm
from .models import Project
from threading import Thread

logger = logging.getLogger(__name__)

class HomeView(View):
    template_name = 'core/index.html'

    def get(self, request):
        form = ContactForm()
        projects = Project.objects.all()
        return render(request, self.template_name, {
            'form': form,
            'projects': projects
        })

class ContactView(View):
    def post(self, request, *args, **kwargs):
        logger.debug("ContactView called")
        logger.debug("Headers: %s", dict(request.headers))
        logger.debug("POST data: %s", request.POST)

        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            logger.warning("Invalid request: missing XHR header")
            return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                send_email_async(
                    'New Portfolio Contact',
                    f"Message from {form.cleaned_data['name']} "
                    f"({form.cleaned_data['email']}):\n\n{form.cleaned_data['message']}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.EMAIL_HOST_USER],
                )
                logger.info("Contact form saved and email sent")
                return JsonResponse({
                    "success": True,
                    "message": "Your message has been sent successfully!"
                })
            except BadHeaderError as e:
                logger.error("BadHeaderError: %s", e)
                return JsonResponse({
                    "success": False,
                    "message": "Invalid header found."
                }, status=500)
            except Exception as e:
                logger.exception("Error sending email")
                return JsonResponse({
                    "success": False,
                    "message": "An error occurred while sending the email. Please try again later."
                }, status=500)

        errors = {field: list(errs) for field, errs in form.errors.items()}
        logger.warning("Form validation failed: %s", errors)
        return JsonResponse({
            "success": False,
            "message": "Invalid form data.",
            "errors": errors
        }, status=400)

def send_email_async(subject, message, from_email, recipient_list):
    def _send():
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error sending email asynchronously")
    Thread(target=_send).start()