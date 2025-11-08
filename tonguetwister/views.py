import sentry_sdk
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (Twister, Articulator, Exercise, Trivia, Funfact, OldPolish, UserProfileArticulator,
                     UserProfileTwister, UserProfileExercise)
from .forms import (ArticulatorForm, ExerciseForm, TwisterForm, TriviaForm, FunfactForm, CustomUserCreationForm,
                    ContactForm, AvatarUploadForm, OldPolishForm)
from .tokens import account_activation_token
from .serializers import OldPolishSerializer, ArticulatorSerializer, FunfactSerializer, TwisterSerializer, \
    ExerciseSerializer, TriviaSerializer
from rest_framework import filters, viewsets
from rest_framework.response import Response
import logging
from asgiref.sync import sync_to_async
from .chatbot import Chatbot
from rest_framework.permissions import IsAuthenticated, AllowAny

logger = logging.getLogger(__name__)  # initialize logger for error handling


# Utility function to check if the user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser


# Main view: loads key objects for the main page
def main(request):
    try:
        # Prepare context data to be displayed on the main page
        context = {
            'twisters': Twister.objects.all()[:1],
            'articulators': Articulator.objects.all()[:1],
            'exercises': Exercise.objects.all()[:1],
            'trivia': Trivia.objects.all()[:0],
            'funfacts': Funfact.objects.all()[:0],
            'old_polish_texts': OldPolish.objects.order_by('?').first(),
        }

        # Add user-specific content if the user is authenticated
        if request.user.is_authenticated:
            context.update({
                'user_twisters_texts': list(UserProfileTwister.objects.filter(user=request.user).select_related('twister').values_list('twister__text', flat=True)),
                'user_articulators_texts': list(UserProfileArticulator.objects.filter(user=request.user).select_related('articulator').values_list('articulator__text', flat=True)),
                'user_exercises_texts': list(UserProfileExercise.objects.filter(user=request.user).select_related('exercise').values_list('exercise__text', flat=True)),
            })

        return render(request, 'tonguetwister/main.html', context)
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return HttpResponse("Internal Server Error", status=500)


# singleton holder
_chatbot_instance = None

def get_chatbot():
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = Chatbot()
    return _chatbot_instance


async def chatbot(request):
    try:
        user_input = request.GET.get('message', '')
        if not user_input:
            return JsonResponse({'response': 'Nie rozumiem.'})

        cached_response = cache.get(user_input)
        if cached_response:
            return JsonResponse({'response': cached_response})

        response = await sync_to_async(get_chatbot().get_response)(user_input)
        cache.set(user_input, response, timeout=3600)
        return JsonResponse({'response': response})
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JsonResponse({'response': 'Wystąpił błąd. Spróbuj ponownie później.'})

@user_passes_test(is_admin)
def content_management(request):
    """View for admin content management."""
    return render(request, 'tonguetwister/admin/settings.html')


def error_404_view(request, exception):
    """Custom view for handling 404 errors."""
    data = {}
    return render(request, 'tonguetwister/404.html', data)


# Utility function for handling "load more" actions for various models
def load_more_generic(request, model, user_profile_model, related_field, limit=1):
    try:
        offset = int(request.GET.get('offset', 0))  # get offset from the request, default is 0
        objects = model.objects.all()[offset:offset + limit]  # get objects based on offset and limit

        if request.user.is_authenticated:
            user_texts = set(user_profile_model.objects.filter(user=request.user).values_list(f'{related_field}__text', flat=True))  # get user's related texts
        else:
            user_texts = set()

        # Prepare data for the response
        data = [{
            'id': obj.id,
            'text': getattr(obj, 'text', ''),  # ensure 'text' is accessed safely
            'is_added': obj.text in user_texts,  # check if the object is already added to the user's list
        } for obj in objects]

        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Exception occured: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


# Specific load more views for different models
def load_more_articulators(request):
    return load_more_generic(request, Articulator, UserProfileArticulator, related_field='articulator')


def load_more_exercises(request):
    return load_more_generic(request, Exercise, UserProfileExercise, related_field='exercise')


def load_more_twisters(request):
    return load_more_generic(request, Twister, UserProfileTwister, related_field='twister')


# Simpler "load more" function for models without user-specific associations
def simple_load_more_generic(request, model, limit=1):
    try:
        offset = int(request.GET.get('offset', 0))  # Get offset from the request
        objects = model.objects.all()[offset:offset + limit]  # Get objects based on offset and limit
        data = list(objects.values())  # Convert objects to list of values
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Exception occured: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


# Load more views for other models
def load_more_trivia(request):
    return simple_load_more_generic(request, Trivia)


def load_more_funfacts(request):
    return simple_load_more_generic(request, Funfact)


# Randomized loading for Old Polish records
def load_more_old_polish(request):
    try:
        # Get a random record from the OldPolish model
        random_record = OldPolish.objects.order_by('?').values().first()
        if random_record:
            return JsonResponse([random_record], safe=False)
        else:
            return JsonResponse([], safe=False)  # Empty response if no records
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


# CRUD Articulators
@user_passes_test(is_admin)
def articulator_list(request):
    articulators = Articulator.objects.all()
    return render(request, 'tonguetwister/articulators/articulator_list.html', {'articulators': articulators})


@user_passes_test(is_admin)
def articulator_add(request):
    if request.method == "POST":
        form = ArticulatorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('articulator_list')
    else:
        form = ArticulatorForm()
    return render(request, 'tonguetwister/articulators/articulator_form.html', {'form': form})


@user_passes_test(is_admin)
def articulator_edit(request, pk):
    articulator = get_object_or_404(Articulator, pk=pk)
    if request.method == "POST":
        form = ArticulatorForm(request.POST, instance=articulator)
        if form.is_valid():
            form.save()
            return redirect('articulator_list')
    else:
        form = ArticulatorForm(instance=articulator)
    return render(request, 'tonguetwister/articulators/articulator_form.html', {'form': form})


@user_passes_test(is_admin)
def articulator_delete(request, pk):
    articulator = get_object_or_404(Articulator, pk=pk)
    if request.method == "POST":
        articulator.delete()
        return redirect('articulator_list')
    return render(request, 'tonguetwister/articulators/articulator_confirm_delete.html', {'articulator': articulator})


# CRUD Exercises
@user_passes_test(is_admin)
def exercise_list(request):
    exercises = Exercise.objects.all()
    return render(request, 'tonguetwister/exercises/exercise_list.html', {'exercises': exercises})


@user_passes_test(is_admin)
def exercise_add(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exercise_list')
    else:
        form = ExerciseForm()
    return render(request, 'tonguetwister/exercises/exercise_form.html', {'form': form})


@user_passes_test(is_admin)
def exercise_edit(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == "POST":
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect('exercise_list')
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'tonguetwister/exercises/exercise_form.html', {'form': form})


@user_passes_test(is_admin)
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == "POST":
        exercise.delete()
        return redirect('exercise_list')
    return render(request, 'tonguetwister/exercises/exercise_confirm_delete.html', {'exercise': exercise})


# CRUD Twisters
@user_passes_test(is_admin)
def twister_list(request):
    twisters = Twister.objects.all()
    return render(request, 'tonguetwister/twisters/twister_list.html', {'twisters': twisters})


@user_passes_test(is_admin)
def twister_add(request):
    if request.method == "POST":
        form = TwisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('twister_list')
    else:
        form = TwisterForm()
    return render(request, 'tonguetwister/twisters/twister_form.html', {'form': form})


@user_passes_test(is_admin)
def twister_edit(request, pk):
    twister = get_object_or_404(Twister, pk=pk)
    if request.method == "POST":
        form = TwisterForm(request.POST, instance=twister)
        if form.is_valid():
            form.save()
            return redirect('twister_list')
    else:
        form = TwisterForm(instance=twister)
    return render(request, 'tonguetwister/twisters/twister_form.html', {'form': form})


@user_passes_test(is_admin)
def twister_delete(request, pk):
    twister = get_object_or_404(Twister, pk=pk)
    if request.method == "POST":
        twister.delete()
        return redirect('twister_list')
    return render(request, 'tonguetwister/twisters/twister_confirm_delete.html', {'twister': twister})


# CRUD Trivia
@user_passes_test(is_admin)
def trivia_list(request):
    trivia = Trivia.objects.all()
    return render(request, 'tonguetwister/trivia/trivia_list.html', {'trivia': trivia})


@user_passes_test(is_admin)
def trivia_add(request):
    if request.method == "POST":
        form = TriviaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('trivia_list')
    else:
        form = TriviaForm()
    return render(request, 'tonguetwister/trivia/trivia_form.html', {'form': form})


@user_passes_test(is_admin)
def trivia_edit(request, pk):
    trivia = get_object_or_404(Trivia, pk=pk)
    if request.method == "POST":
        form = TriviaForm(request.POST, instance=trivia)
        if form.is_valid():
            form.save()
            return redirect('trivia_list')
    else:
        form = TriviaForm(instance=trivia)
    return render(request, 'tonguetwister/trivia/trivia_form.html', {'form': form})


@user_passes_test(is_admin)
def trivia_delete(request, pk):
    t = get_object_or_404(Trivia, pk=pk)
    if request.method == "POST":
        t.delete()
        return redirect('trivia_list')
    return render(request, 'tonguetwister/trivia/trivia_confirm_delete.html', {'t': t})


# CRUD Fun Facts
@user_passes_test(is_admin)
def funfact_list(request):
    funfacts = Funfact.objects.all()
    return render(request, 'tonguetwister/funfacts/funfact_list.html', {'funfacts': funfacts})


@user_passes_test(is_admin)
def funfact_add(request):
    if request.method == "POST":
        form = FunfactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('funfact_list')
    else:
        form = FunfactForm()
    return render(request, 'tonguetwister/funfacts/funfact_form.html', {'form': form})


@user_passes_test(is_admin)
def funfact_edit(request, pk):
    funfact = get_object_or_404(Funfact, pk=pk)
    if request.method == "POST":
        form = FunfactForm(request.POST, instance=funfact)
        if form.is_valid():
            form.save()
            return redirect('funfact_list')
    else:
        form = FunfactForm(instance=funfact)
    return render(request, 'tonguetwister/funfacts/funfact_form.html', {'form': form})


@user_passes_test(is_admin)
def funfact_delete(request, pk):
    funfact = get_object_or_404(Funfact, pk=pk)
    if request.method == "POST":
        funfact.delete()
        return redirect('funfact_list')
    return render(request, 'tonguetwister/funfacts/funfact_confirm_delete.html', {'funfact': funfact})


# CRUD Old-new Polish
@user_passes_test(is_admin)
def oldpolish_list(request):
    oldpolishs = OldPolish.objects.all()
    return render(request, 'tonguetwister/oldpolishs/oldpolish_list.html', {'oldpolishs': oldpolishs})


@user_passes_test(is_admin)
def oldpolish_add(request):
    if request.method == "POST":
        form = OldPolishForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('oldpolish_list')
    else:
        form = OldPolishForm()
    return render(request, 'tonguetwister/oldpolishs/oldpolish_form.html', {'form': form})


@user_passes_test(is_admin)
def oldpolish_edit(request, pk):
    oldpolish = get_object_or_404(OldPolish, pk=pk)
    if request.method == "POST":
        form = OldPolishForm(request.POST, instance=oldpolish)
        if form.is_valid():
            form.save()
            return redirect('oldpolish_list')
    else:
        form = OldPolishForm(instance=oldpolish)
    return render(request, 'tonguetwister/oldpolishs/oldpolish_form.html', {'form': form})


@user_passes_test(is_admin)
def oldpolish_delete(request, pk):
    oldpolish = get_object_or_404(OldPolish, pk=pk)
    if request.method == "POST":
        oldpolish.delete()
        return redirect('oldpolish_list')
    return render(request, 'tonguetwister/oldpolishs/oldpolish_confirm_delete.html', {'oldpolish': oldpolish})


@login_required
def user_content(request):
    """
    User content view to handle avatar upload, deletion, and display user's articulators, exercises, and twisters.
    """
    profile = request.user.profile

    # Handle avatar deletion
    if request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'delete-avatar':
            if profile.avatar:
                profile.avatar.delete(save=True)
            else:
                return redirect('user_content')

        # Handle avatar upload
        form = AvatarUploadForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('user_content')
    else:
        form = AvatarUploadForm(instance=request.user.profile)

    # Fetch all articulators, exercises, and twisters with user-specific content
    all_articulators = Articulator.objects.all()
    user_articulators = UserProfileArticulator.objects.filter(user=request.user).select_related('articulator')
    user_articulators_texts = list(
        UserProfileArticulator.objects.filter(user=request.user).values_list('articulator__text', flat=True))
    all_exercises = Exercise.objects.all()
    user_exercises = UserProfileExercise.objects.filter(user=request.user).select_related('exercise')
    user_exercises_texts = list(
        UserProfileExercise.objects.filter(user=request.user).values_list('exercise__text', flat=True))
    all_twisters = Twister.objects.all()
    user_twisters = UserProfileTwister.objects.filter(user=request.user).select_related('twister')
    user_twisters_texts = list(
        UserProfileTwister.objects.filter(user=request.user).values_list('twister__text', flat=True))

    context = {
        'form': form,
        'articulators': all_articulators,
        'user_articulators': user_articulators,
        'user_articulators_texts': user_articulators_texts,
        'exercises': all_exercises,
        'user_exercises': user_exercises,
        'user_exercises_texts': user_exercises_texts,
        'twisters': all_twisters,
        'user_twisters': user_twisters,
        'user_twisters_texts': user_twisters_texts,
    }

    # Handle export of user exercises as a PDF
    if 'export' in request.GET and request.GET['export'] == 'exercises':

        # Create a simple PDF with the rendered HTML content
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="lingwolamkowe-cwiczenia.pdf"'

        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from django.utils.html import strip_tags
        import os

        # rejestracja Arial.ttf
        font_path = os.path.join(
            settings.BASE_DIR,
            "tonguetwister",
            "static",
            "tonguetwister",
            "fonts",
            "arial.ttf"
        )
        pdfmetrics.registerFont(TTFont("Arial", font_path))

        # Prepare PDF document
        pdf = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="PolishNormal", fontName="Arial", fontSize=12))
        styles.add(ParagraphStyle(name="PolishHeading", fontName="Arial", fontSize=14, spaceAfter=12))
        story = []

        # Convert the HTML into plain text and add it to the PDF content
        story.append(Paragraph("Rozgrzewanie artykulatorów", styles["PolishHeading"]))
        for art in context['user_articulators_texts']:
            plain_text = strip_tags(art)
            story.append(Paragraph(plain_text, styles["PolishNormal"]))
            story.append(Spacer(1, 12))

        story.append(Paragraph("Ćwiczenia właściwe", styles["PolishHeading"]))
        for exercise in context['user_exercises_texts']:
            plain_text = strip_tags(exercise)
            story.append(Paragraph(plain_text, styles["PolishNormal"]))
            story.append(Spacer(1, 12))

        story.append(Paragraph("Łamańce językowe", styles["PolishHeading"]))
        for twister in context['user_twisters_texts']:
            plain_text = strip_tags(twister)
            story.append(Paragraph(plain_text, styles["PolishNormal"]))
            story.append(Spacer(1, 12))

        # Build the PDF
        pdf.build(story)
        return response

    return render(request, 'tonguetwister/users/user-content.html', context)


# Add/delete Articulators
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_articulator(request, articulator_id):
    user = request.user
    articulator = get_object_or_404(Articulator, id=articulator_id)
    if UserProfileArticulator.objects.filter(user=user, articulator=articulator).exists():
        return JsonResponse({'status': 'Duplicate articulator'})
    user_articulator = UserProfileArticulator.objects.create(user=user, articulator=articulator)
    return JsonResponse({'status': 'Articulator added', 'userArticulatorId': user_articulator.id})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_articulator(request, articulator_id):
    user = request.user
    articulator = get_object_or_404(UserProfileArticulator, id=articulator_id, user=user)
    articulator.delete()
    return JsonResponse({'status': 'Articulator deleted'})


# Add/delete Exercises
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_exercise(request, exercise_id):
    user = request.user
    exercise = get_object_or_404(Exercise, id=exercise_id)
    if UserProfileExercise.objects.filter(user=user, exercise=exercise).exists():
        return JsonResponse({'status': 'Duplicate exercise'})
    user_exercise = UserProfileExercise.objects.create(user=user, exercise=exercise)
    return JsonResponse({'status': 'Exercise added', 'userExerciseId': user_exercise.id})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(UserProfileExercise, id=exercise_id, user=request.user)
    exercise.delete()
    return JsonResponse({'status': 'Exercise deleted'})


# Add/delete Twisters
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_twister(request, twister_id):
    user = request.user
    twister = get_object_or_404(Twister, id=twister_id)
    if UserProfileTwister.objects.filter(user=user, twister=twister).exists():
        return JsonResponse({'status': 'Duplicate twister'})
    user_twister = UserProfileTwister.objects.create(user=user, twister=twister)
    return JsonResponse({'status': 'Twister added', 'userTwisterId': user_twister.id})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_twister(request, twister_id):
    twister = get_object_or_404(UserProfileTwister, id=twister_id, user=request.user)
    twister.delete()
    return JsonResponse({'status': 'Twister deleted'})


def login_view(request):
    # Initializes an authentication form for user login
    form = AuthenticationForm()
    login_attempts_key = f"login_attempts_{request.META.get('REMOTE_ADDR')}"
    login_attempts = cache.get(login_attempts_key, 0)

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)  # populates form with submitted data

        if form.is_valid():
            # Retrieves the username and password from cleaned data (validated form data)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticates the user using Django's authentication system
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Logs the user in if authentication is successful
                login(request, user)
                cache.delete(login_attempts_key)  # reset login attempts on success
                return redirect('main')  # redirects to the 'main' view after login
            else:
                login_attempts += 1
                cache.set(login_attempts_key, login_attempts, timeout=300)  # 5 min lock
                messages.error(request, 'Napotkaliśmy zgoła nieoczekiwane błędy 😱 spróbuj raz jeszcze 😊')

                if login_attempts >= 5:
                    messages.error(request, 'Zbyt wiele nieudanych prób logowania. Spróbuj ponownie za 5 minut.')
                    return redirect('login')

    return render(request, 'tonguetwister/registration/login.html', {'form': form})


def send_activation_email(user, request):
    try:
        # Prepares the email subject and token for account activation
        subject = 'Witamy na pokładzie!'
        token = account_activation_token.make_token(user)  # generates an activation token for the user
        uid = urlsafe_base64_encode(force_bytes(user.pk))  # encodes the user's primary key

        # Builds the activation link with the user's uid and token
        activation_link = request.build_absolute_uri(reverse('activate', args=[uid, token]))

        # Renders an HTML template for the email body and generates a plain text version
        html_message = render_to_string('tonguetwister/registration/activation.html', {'user': user, 'activation_link': activation_link})
        plain_message = strip_tags(html_message)

        # Sets the sender's email and recipient (user's email)
        from_email = settings.EMAIL_HOST_USER
        to = user.email

        # Sends the email with both HTML and plain text versions
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Błąd przy wysyłaniu e-maila: {e}")

def register_view(request):
    # Handles user registration via POST request
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # custom form for user registration

        if form.is_valid():
            # Saves the new user and sends them an activation email
            user = form.save()
            send_activation_email(user, request)
            # Shows a success message and redirects to the login page
            messages.success(request,
                             'Brawo! Możesz się zalogować. Sprawdź swoją skrzynkę e-mail, aby aktywować konto.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return render(request, 'tonguetwister/registration/register.html', {'form': form})
    else:
        # If not a POST request, renders an empty registration form
        form = CustomUserCreationForm()
    return render(request, 'tonguetwister/registration/register.html', {'form': form})


def activate(request, uidb64, token):
    # Attempts to decode the user ID from the URL-safe base64 string
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)  # retrieves the user based on the decoded UID
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Checks if the user exists and the activation token is valid
    if user is not None and account_activation_token.check_token(user, token):
        # Marks the user's email as confirmed and saves the profile
        user.profile.email_confirmed = True
        user.profile.save()
        messages.success(request, 'Dziękujemy za potwierdzenie :) Twoje konto zostało zweryfikowane.')
        return redirect('login')
    else:
        messages.error(request, 'Link aktywacyjny jest nieprawidłowy!')
        return redirect('register')


@csrf_protect
def password_reset_view(request):
    # Handles the password reset process
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Tries to find the user based on the provided email
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)  # generates a reset token
            uid = urlsafe_base64_encode(force_bytes(user.pk))  # encodes the user's ID

            # Hold token in redis
            cache.set(f'password_reset_{uid}', token, timeout=600)  # 10 min

            # Constructs a password reset link and email message
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[uid, token])
            )
            plain_message = f"""
            Resetuj hasło

            Czołem {user.username},

            Otrzymaliśmy prośbę o zresetowanie hasła do Twojego konta. Kliknij poniższy link, aby je zresetować:
            {reset_link}

            Jeśli to nie Ty prosiłeś o zresetowanie hasła, po prostu zignoruj tę wiadomość. Twoje hasło pozostanie bez zmian.

            Pozdrawiamy,
            Zespół LingwoŁamki
            """
            context = {'reset_link': reset_link, 'user': user}
            html_message = render_to_string('tonguetwister/registration/password_reset_email.html', context)

            # Sends the password reset email
            subject = 'Resetuj swoje hasło'
            from_email = settings.EMAIL_HOST_USER
            send_mail(
                subject,
                plain_message,
                from_email,
                [email],
                html_message=html_message
            )
            return redirect('password_reset_done')
        except User.DoesNotExist:
            sentry_sdk.capture_message(f'Nieudana próba resetowania hasła dla: {email}', level='warning')
            messages.error(request, 'Nie znaleziono użytkownika z tym adresem email.')
    return render(request, 'tonguetwister/registration/password_reset_form.html')


@csrf_protect
def password_reset_confirm_view(request, uidb64, token):
    # Handles confirmation of password reset
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))  # decodes the UID
        user = User.objects.get(pk=uid)  # retrieves the user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # If token is valid, the user can reset their password
        if request.method == 'POST':
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            if new_password1 == new_password2:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)  # Prevents logout after password reset
                messages.success(request, 'Twoje hasło zostało zmienione.')
                return redirect('password_reset_complete')
            else:
                messages.error(request, 'Hasła nie są identyczne.')
        return render(request, 'tonguetwister/registration/password_reset_confirm.html')
    else:
        messages.error(request, 'Link resetowania hasła jest nieprawidłowy.')
        return redirect('password_reset')


@csrf_protect
def password_reset_complete_view(request):
    return render(request, 'tonguetwister/registration/password_reset_complete.html')


@csrf_protect
def password_reset_done_view(request):
    return render(request, 'tonguetwister/registration/password_reset_done.html')


def contact(request):
    # Handles the contact form submission
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            # Retrieves data from the cleaned form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            subject = f'Kontakt od {name}'
            message_with_email = f"Od: {email}\n\n{message}"

            try:
                # Sends the contact email
                send_mail(
                    subject=subject,
                    message=message_with_email,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, 'Twoja wiadomość została Nam przekazana')
            except Exception as e:
                messages.error(request, f'Błąd przy wysyłaniu wiadomości: {e}')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'tonguetwister/partials/static/contact.html', {'form': form})

CACHE_TIMEOUT = 60 * 5  # 5 min

class OldPolishViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Old Polish phrases"""
    queryset = OldPolish.objects.all()
    serializer_class = OldPolishSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['old_text', 'new_text']
    permission_classes = [AllowAny]

    @method_decorator(cache_page(CACHE_TIMEOUT, cache="default"))
    @extend_schema(
        parameters=[
            {
                "name": "search",
                "in": "query",
                "description": "Search for Old Polish phrases",
                "schema": {"type": "string"},
            }
        ],
        responses={200: OldPolishSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response if response.data else Response({"detail": "No results found"}, status=404)

class ArticulatorViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for articulators"""
    queryset = Articulator.objects.all()
    serializer_class = ArticulatorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']
    permission_classes = [AllowAny]

    @method_decorator(cache_page(CACHE_TIMEOUT, cache="default"))
    @extend_schema(
        parameters=[
            {
                "name": "search",
                "in": "query",
                "description": "Search for Articulator phrases",
                "schema": {"type": "string"},
            }
        ],
        responses={200: ArticulatorSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response if response.data else Response({"detail": "No results found"}, status=404)

class FunfactViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for funfacts"""
    queryset = Funfact.objects.all()
    serializer_class = FunfactSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(CACHE_TIMEOUT, cache="default"))
    @extend_schema(
        parameters=[
            {
                "name": "search",
                "in": "query",
                "description": "Search for Funfact phrases",
                "schema": {"type": "string"},
            }
        ],
        responses={200: FunfactSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response if response.data else Response({"detail": "No results found"}, status=404)

class TwisterViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for twisters"""
    queryset = Twister.objects.all()
    serializer_class = TwisterSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']
    permission_classes = [AllowAny]

    @method_decorator(cache_page(CACHE_TIMEOUT, cache="default"))
    @extend_schema(
        parameters=[
            {
                "name": "search",
                "in": "query",
                "description": "Search for Twister phrases",
                "schema": {"type": "string"},
            }
        ],
        responses={200: TwisterSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response if response.data else Response({"detail": "No results found"}, status=404)

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for exercises"""
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']
    permission_classes = [AllowAny]

    @method_decorator(cache_page(CACHE_TIMEOUT, cache="default"))
    @extend_schema(
        parameters=[
            {
                "name": "search",
                "in": "query",
                "description": "Search for Exercise phrases",
                "schema": {"type": "string"},
            }
        ],
        responses={200: ExerciseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response if response.data else Response({"detail": "No results found"}, status=404)

class TriviaViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for trivias"""
    queryset = Trivia.objects.all()
    serializer_class = TriviaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']
    permission_classes = [AllowAny]

    @method_decorator(cache_page(CACHE_TIMEOUT, cache="default"))
    @extend_schema(
        parameters=[
            {
                "name": "search",
                "in": "query",
                "description": "Search for Trivia phrases",
                "schema": {"type": "string"},
            }
        ],
        responses={200: TriviaSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response if response.data else Response({"detail": "No results found"}, status=404)

class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        tags=["Authentication"],
        summary="Zaloguj i pobierz token JWT",
        description="Podaj login i hasło, aby otrzymać JWT access i refresh token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=200)
