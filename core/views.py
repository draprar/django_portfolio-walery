import logging

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.utils.html import escape

from django_ratelimit.decorators import ratelimit

from analytics.utils import count_visit
from .forms import ContactForm
from .models import Project
from .email import send_brevo_email

logger = logging.getLogger(__name__)


@count_visit
def index(request):
    return render(request, "core/index.html")


def health_check(request):
    return JsonResponse({"status": "ok"})


class HomeView(View):
    template_name = "core/index.html"

    def get(self, request):
        form = ContactForm()
        projects = Project.objects.all()
        return render(request, self.template_name, {"form": form, "projects": projects})


@method_decorator(ratelimit(key="ip", rate="5/m", block=True), name="dispatch")
class ContactView(View):
    """
    Secure contact endpoint:
    - rate-limited (5 requests/min per IP) via django-ratelimit
    - rejects non-AJAX requests (X-Requested-With)
    - simple honeypot check for hidden 'website' field
    - does not log PII or message body
    """

    def post(self, request, *args, **kwargs):
        # Basic XHR check (case-insensitive)
        if request.headers.get("x-requested-with", "").lower() != "xmlhttprequest":
            logger.warning("Contact attempt rejected: missing or invalid XHR header from %s",
                           request.META.get("REMOTE_ADDR"))
            return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

        # Honeypot: invisible field that bots often fill
        if request.POST.get("website"):
            logger.warning("Honeypot triggered from %s", request.META.get("REMOTE_ADDR"))
            # return a generic success-looking response to reduce bot feedback
            return JsonResponse({"success": False, "message": "Invalid form data."}, status=400)

        form = ContactForm(request.POST)

        # Log only IP and validation result. Do NOT log form data or message content.
        logger.debug("Contact form submitted from %s. Valid: %s",
                     request.META.get("REMOTE_ADDR"), form.is_valid())

        if not form.is_valid():
            errors = {field: list(errs) for field, errs in form.errors.items()}
            logger.warning("Invalid contact form from %s. Errors: %s",
                           request.META.get("REMOTE_ADDR"), errors)
            return JsonResponse({
                "success": False,
                "message": "Invalid form data.",
                "errors": errors
            }, status=400)

        # At this point form is valid. Save and send email.
        try:
            # Persist (but avoid logging saved content)
            form.save()

            subject = "Kontakt"
            # Build email body from cleaned_data. We must include the message in the mail,
            # but do not log the content anywhere.
            name = form.cleaned_data.get("name", "Unknown")
            email = form.cleaned_data.get("email", "")
            message_body = form.cleaned_data.get("message", "")

            safe_message = escape(message_body).replace("\n", "<br>")

            html_content = f"""
                <p><strong>Message from:</strong> {escape(name)}</p>
                <p><strong>Email:</strong> {escape(email)}</p>
                <p>{safe_message}</p>
            """

            recipient_list = [settings.DEFAULT_FROM_EMAIL]

            result = send_brevo_email(subject, html_content, recipient_list)

            if result:
                logger.info("Contact form processed successfully from %s", request.META.get("REMOTE_ADDR"))
                return JsonResponse({
                    "success": True,
                    "message": "Your message has been sent successfully!"
                })
            else:
                logger.error("Email sending failed for contact from %s", request.META.get("REMOTE_ADDR"))
                return JsonResponse({
                    "success": False,
                    "message": "Email service failed, please try again later."
                }, status=500)

        except Exception:
            # logger.exception records traceback but avoid attaching user content
            logger.exception("Unhandled error processing contact form from %s", request.META.get("REMOTE_ADDR"))
            return JsonResponse({
                "success": False,
                "message": "An error occurred while sending the email. Please try again later."
            }, status=500)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=["POST"])
