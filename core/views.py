from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
import logging

from .forms import ContactForm
from .models import Project
from .email import send_brevo_email   # <- zamiast send_mail

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

                subject = "New Portfolio Contact"
                html_content = f"""
                    <h2>Message from {form.cleaned_data['name']}</h2>
                    <p><strong>Email:</strong> {form.cleaned_data['email']}</p>
                    <p>{form.cleaned_data['message']}</p>
                """
                recipient_list = [settings.DEFAULT_FROM_EMAIL]  # możesz zmienić na swój adres

                result = send_brevo_email(subject, html_content, recipient_list)

                if result:
                    logger.info("Contact form saved and Brevo email sent")
                    return JsonResponse({
                        "success": True,
                        "message": "Your message has been sent successfully!"
                    })
                else:
                    logger.error("Brevo email sending failed")
                    return JsonResponse({
                        "success": False,
                        "message": "Email service failed, please try again later."
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