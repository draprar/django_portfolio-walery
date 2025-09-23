from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import logging
from .forms import ContactForm
from django.urls import reverse
from .models import Project

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

    def post(self, request):
        form = ContactForm(request.POST)
        projects = Project.objects.all()
        if form.is_valid():
            try:
                form.save()
                send_mail(
                    'New Portfolio Contact',
                    f"Message from {form.cleaned_data['name']} "
                    f"({form.cleaned_data['email']}):\n\n{form.cleaned_data['message']}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.EMAIL_HOST_USER],
                )
                messages.success(
                    request,
                    '<div data-en="Your message has been sent successfully!" '
                    'data-pl="Twoja wiadomość została wysłana pomyślnie!">'
                    'Your message has been sent successfully!</div>'
                )
            except BadHeaderError as e:
                logger.error(f"BadHeaderError: {e}")
                messages.error(
                    request,
                    '<div data-en="Invalid header found." '
                    'data-pl="Wykryto nieprawidłowy nagłówek.">'
                    'Invalid header found.</div>'
                )
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                messages.error(
                    request,
                    '<div data-en="An error occurred while sending the email. Please try again later." '
                    'data-pl="Wystąpił błąd podczas wysyłania wiadomości. Spróbuj ponownie później.">'
                    'An error occurred while sending the email. Please try again later.</div>'
                )

            return redirect(f"{reverse('home')}#contact")

        return render(request, self.template_name, {
            'form': form,
            'projects': projects
        })