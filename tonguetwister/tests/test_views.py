import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User, Group
from django.contrib.messages import get_messages
from django.test import AsyncClient, Client
from tonguetwister.models import Twister, Articulator, Exercise, Trivia, Funfact, OldPolish, UserProfileTwister, UserProfileArticulator, UserProfileExercise
from tonguetwister.views import get_chatbot
from tonguetwister.forms import ContactForm, AvatarUploadForm
from tonguetwister.tokens import account_activation_token


# Tests for main view responses and context in various states
@pytest.mark.django_db
class TestMainViews:
    def test_main_unauthenticated(self, client):
        # Unauthenticated main view access, checks status and base template
        url = reverse('main')
        response = client.get(url)

        # Verifies all necessary context data for unauthenticated user
        assert response.status_code == 200
        assert 'tonguetwister/main.html' in [t.name for t in response.templates]

        assert 'twisters' in response.context
        assert 'articulators' in response.context
        assert 'exercises' in response.context
        assert 'trivia' in response.context
        assert 'funfacts' in response.context
        assert 'old_polish_texts' in response.context

        assert 'user_twisters_texts' not in response.context
        assert 'user_articulators_texts' not in response.context
        assert 'user_exercises_texts' not in response.context

    def test_main_authenticated(self, client, django_user_model):
        # Authenticated main view access, checks additional user context
        user = django_user_model.objects.create_user(username='testuser', password='password')
        client.login(username=user.username, password='password')
        url = reverse('main')
        response = client.get(url)

        # Verifies context data for authenticated user
        assert response.status_code == 200
        assert 'tonguetwister/main.html' in [t.name for t in response.templates]

        assert 'twisters' in response.context
        assert 'articulators' in response.context
        assert 'exercises' in response.context
        assert 'trivia' in response.context
        assert 'funfacts' in response.context
        assert 'old_polish_texts' in response.context
        assert 'user_twisters_texts' in response.context
        assert 'user_articulators_texts' in response.context
        assert 'user_exercises_texts' in response.context

    def test_main_view_internal_server_error(self, client, mocker):
        # Simulates server error in main view and verifies error response
        url = reverse('main')
        mocker.patch('tonguetwister.views.Twister.objects.all', side_effect=Exception("Test Exception"))
        response = client.get(url)

        assert response.status_code == 500
        assert "Internal Server Error" in response.content.decode()


@pytest.mark.django_db
class TestContentManagementViews:

    @pytest.fixture
    def admin_user(self):
        # Creates admin user fixture
        return User.objects.create_superuser(username='adminuser', password='adminpassword', email='admin@example.com', is_staff=True)

    @pytest.fixture
    def regular_user(self):
        # Creates regular user fixture
        return User.objects.create_user(username='user', password='userpassword', email='user@example.com')

    def test_content_management_unauthenticated(self, client):
        # Tests redirect for unauthenticated access to content management
        url = reverse('content_management')
        response = client.get(url)

        assert response.status_code == 302

    def test_content_management_user(self, client, regular_user):
        # Tests redirect for regular user access to content management
        client.login(username='user', password='userpassword')
        url = reverse('content_management')
        response = client.get(url)

        assert response.status_code == 302

    def test_content_management_admin(self, client, admin_user):
        # Tests content management view access for admin user
        client.force_login(admin_user)
        url = reverse('content_management')
        response = client.get(url)

        assert response.status_code == 200
        assert 'tonguetwister/admin/settings.html' in [t.name for t in response.templates]

    @pytest.fixture(params=[
        # Parametrizes test data for different content types
        ('articulator_list', 'articulator_add', 'articulator_edit', 'articulator_delete', Articulator),
        ('exercise_list', 'exercise_add', 'exercise_edit', 'exercise_delete', Exercise),
        ('twister_list', 'twister_add', 'twister_edit', 'twister_delete', Twister),
        ('trivia_list', 'trivia_add', 'trivia_edit', 'trivia_delete', Trivia),
        ('funfact_list', 'funfact_add', 'funfact_edit', 'funfact_delete', Funfact),
        ('oldpolish_list', 'oldpolish_add', 'oldpolish_edit', 'oldpolish_delete', OldPolish),
    ])
    def model_data(self, request):
        # Provides model data for list, add, edit, and delete tests
        return request.param

    def test_list_view(self, client, model_data):
        # Tests list view access redirect for unauthenticated users
        list_url = reverse(model_data[0])
        response = client.get(list_url)

        assert response.status_code == 302

    def test_list_view_user(self, client, regular_user, model_data):
        # Tests list view access redirect for regular users
        client.login(username='user', password='userpassword')
        list_user_url = reverse(model_data[0])
        response = client.get(list_user_url)

        assert response.status_code == 302

    def test_list_view_admin(self, client, admin_user, model_data):
        # Tests list view access for admin users
        client.force_login(admin_user)
        list_admin_url = reverse(model_data[0])
        response = client.get(list_admin_url)

        assert response.status_code == 200

    def test_add_view(self, client, admin_user, model_data):
        # Tests add view with POST data for admin user
        client.force_login(admin_user)
        add_url = reverse(model_data[1])
        if model_data[1] == 'oldpolish_add':
            form_data = {'old_text': 'old_text', 'new_text': 'new_text'}
        else:
            form_data = {'text': 'test'}
        response = client.post(add_url, data=form_data)

        assert response.status_code == 302

    def test_edit_view(self, client, admin_user, model_data):
        # Tests edit view with POST data for admin user
        client.force_login(admin_user)
        if model_data[2] == 'oldpolish_edit':
            model_instance = model_data[4].objects.create(old_text='old_text', new_text='new_text')
        else:
            model_instance = model_data[4].objects.create(text='test')
        edit_url = reverse(model_data[2], args=[model_instance.pk])
        if model_data[2] == 'oldpolish_edit':
            form_data = {'old_text': 'new_old_text', 'new_text': 'new_new_text'}
        else:
            form_data = {'text': 'new_test'}
        response = client.post(edit_url, data=form_data)

        assert response.status_code == 302

    def test_delete_view(self, client, admin_user, model_data):
        # Tests delete view for admin user and checks if item is deleted
        client.force_login(admin_user)
        if model_data[3] == 'oldpolish_delete':
            model_instance = model_data[4].objects.create(old_text='old_text', new_text='new_text')
        else:
            model_instance = model_data[4].objects.create(text='test')
        delete_url = reverse(model_data[3], args=[model_instance.pk])
        response = client.post(delete_url)

        assert response.status_code == 302
        assert not model_data[4].objects.filter(pk=model_instance.pk).exists()


@pytest.mark.django_db
class TestLoadMoreGenerics:

    @pytest.fixture(params=[
        ('load_more_articulators', Articulator, UserProfileArticulator, 'articulator'),
        ('load_more_exercises', Exercise, UserProfileExercise, 'exercise'),
        ('load_more_twisters', Twister, UserProfileTwister, 'twister'),
    ])
    def model_data(self, request):
        # Fixture for load-more functionality, with model and related user profile models
        return request.param

    def test_load_more_generic_unauthenticated(self, client, model_data):
        # Tests unauthenticated load-more view response and expected JSON output
        url = reverse(model_data[0])
        model_class = model_data[1]
        model_class.objects.create(text='Test text')

        response = client.get(url, {'offset': 0})

        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        assert len(response.json()) == 1
        assert response.json()[0]['text'] == 'Test text'
        assert response.json()[0]['is_added'] is False

    def test_load_more_generic_authenticated(self, client, model_data, django_user_model):
        # Tests authenticated load-more view, with user profile association
        user = django_user_model.objects.create_user(username='testuser', password='testpassword')
        client.login(username=user.username, password='testpassword')
        url = reverse(model_data[0])
        model_class = model_data[1]
        user_profile_model = model_data[2]
        related_field = model_data[3]

        instance = model_class.objects.create(text='Test text')
        user_profile_model.objects.create(user=user, **{related_field: instance})

        response = client.get(url, {'offset': 0})

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['text'] == 'Test text'
        assert response.json()[0]['is_added'] is True

    def test_load_more_generic_internal_server_error(self, client, mocker, model_data):
        # Simulates internal server error on load-more view request
        url = reverse(model_data[0])
        mocker.patch(f'tonguetwister.models.{model_data[1].__name__}.objects.all', side_effect=Exception("Test Exception"))

        response = client.get(url)

        assert response.status_code == 500
        assert response.json() == {'error': 'Internal Server Error'}


@pytest.mark.django_db
class TestSimpleLoadMoreGenerics:

    @pytest.fixture(params=[
        ('load_more_trivia', Trivia),
        ('load_more_funfacts', Funfact),
    ])
    def model_data(self, request):
        # Fixture for simple load-more views for trivia and fun facts
        return request.param

    def test_simple_load_more_generic(self, client, model_data):
        # Tests simple load-more view response and JSON output
        url = reverse(model_data[0])
        model_class = model_data[1]
        model_class.objects.create(text='Test text')

        response = client.get(url)

        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        assert len(response.json()) == 1
        assert response.json()[0]['text'] == 'Test text'

    def test_simple_load_more_generic_internal_error(self, client, mocker, model_data):
        # Simulates internal server error on simple load-more view request
        url = reverse(model_data[0])
        mocker.patch(f'tonguetwister.models.{model_data[1].__name__}.objects.all', side_effect=Exception("Test Exception"))

        response = client.get(url)

        assert response.status_code == 500
        assert response.json() == {'error': 'Internal Server Error'}


@pytest.mark.django_db
class TestLoadMoreOldPolish:

    def test_load_more_old_polish(self, client):
        # Tests load-more view for OldPolish model and verifies JSON output
        url = reverse('load_more_old_polish')

        # Create a test record for OldPolish model
        OldPolish.objects.create(old_text='old_text', new_text='new_text')

        response = client.get(url)

        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        assert len(response.json()) == 1
        assert response.json()[0]['old_text'] == 'old_text'
        assert response.json()[0]['new_text'] == 'new_text'

    def test_load_more_old_polish_internal_error(self, client, mocker):
        # Simulates internal server error on OldPolish load-more view request
        url = reverse('load_more_old_polish')

        # Mocking order_by method to raise an exception
        mocker.patch('tonguetwister.models.OldPolish.objects.order_by', side_effect=Exception("Test Exception"))

        response = client.get(url)

        # Assert that the view returns a 500 status code and correct error message
        assert response.status_code == 500
        assert response.json() == {'error': 'Internal Server Error'}


@pytest.mark.django_db
class TestUserContent:

    @pytest.fixture
    def regular_user_and_profile(self, django_user_model):
        # Fixture for creating a user and associated profile
        user = django_user_model.objects.create_user(username='user', password='userpassword', email='user@example.com')
        profile = user.profile
        return user, profile

    def test_user_content_view_loads_correctly(self, client, regular_user_and_profile):
        # Test that user content view loads with correct context variables and template
        user, profile = regular_user_and_profile
        client.login(username='user', password='userpassword')
        url = reverse('user_content')
        response = client.get(url)

        assert response.status_code == 200
        assert 'tonguetwister/users/user-content.html' in [t.name for t in response.templates]
        assert 'articulators' in response.context
        assert 'exercises' in response.context
        assert 'twisters' in response.context


@pytest.mark.parametrize('params', [
    (Articulator, UserProfileArticulator, 'add_articulator', 'delete_articulator'),
    (Exercise, UserProfileExercise, 'add_exercise', 'delete_exercise'),
    (Twister, UserProfileTwister, 'add_twister', 'delete_twister')
])
@pytest.mark.django_db
class TestUserObjectViews:

    @pytest.fixture
    def regular_user(self, django_user_model):
        # Fixture for creating a regular user
        return django_user_model.objects.create_user(username='user', password='userpassword', email='user@example.com')

    def test_add_object(self, client, params, regular_user):
        # Test adding an object to user profile
        client.login(username='user', password='userpassword')
        model, user_model, add_url, delete_url = params
        obj = model.objects.create(text='test')

        url = reverse(add_url, args=[obj.id])
        response = client.post(url)

        assert response.status_code == 200
        assert user_model.objects.filter(user=regular_user, **{model.__name__.lower(): obj}).exists()
        assert response.json()['status'] == f"{model.__name__} added"

    def test_add_duplicate_object(self, client, params, regular_user):
        # Test adding duplicate object to user profile returns appropriate response
        client.login(username='user', password='userpassword')
        model, user_model, add_url, delete_url = params
        obj = model.objects.create(text='text')
        user_model.objects.create(user=regular_user, **{model.__name__.lower(): obj})

        url = reverse(add_url, args=[obj.id])
        response = client.post(url)

        assert response.status_code == 200
        assert response.json()['status'] == f"Duplicate {model.__name__.lower()}"

    def test_delete_object(self, client, params, regular_user):
        # Test deleting an object from user profile
        client.login(username='user', password='userpassword')
        model, user_model, add_url, delete_url = params
        obj = model.objects.create(text='text')
        user_obj = user_model.objects.create(user=regular_user, **{model.__name__.lower(): obj})

        url = reverse(delete_url, args=[user_obj.id])
        response = client.post(url)

        assert response.status_code == 200
        assert not user_model.objects.filter(id=user_obj.id).exists()
        assert response.json()['status'] == f"{model.__name__} deleted"


@pytest.mark.django_db
class TestAuthViews:

    @pytest.fixture
    def regular_user(self, django_user_model):
        # Fixture for creating an active user
        return django_user_model.objects.create_user(username='user', email='user@example.com', password='testpassword', is_active=True)

    @pytest.fixture
    def new_user(self):
        # Fixture for valid new user data for registration
        return {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Str0ngP@ssw0rd!',
            'password2': 'Str0ngP@ssw0rd!'
        }

    @pytest.fixture
    def new_user_invalid(self):
        # Fixture for invalid new user data for registration
        return {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password123',
            'password2': 'password'
        }

    @pytest.fixture
    def regular_users_group(self):
        # Fixture for creating Regular Users group
        Group.objects.create(name='Regular Users')

    def test_login_view_valid(self, client, regular_user):
        # Test valid login redirects to main page
        login_data = {'username': regular_user.username, 'password': 'testpassword'}
        response = client.post(reverse('login'), data=login_data)

        assert response.status_code == 302
        assert response.url == reverse('main')

    def test_login_view_invalid(self, client, regular_user):
        # Test invalid login shows correct response without redirection
        login_data = {'username': regular_user.username, 'password': 'wrongpassword'}
        response = client.post(reverse('login'), data=login_data)

        assert response.status_code == 200

    def test_register_view_valid(self, client, new_user, regular_users_group):
        # Test valid registration redirects to login and sends confirmation email
        response = client.post(reverse('register'), data=new_user)

        assert response.status_code == 302
        assert response.url == reverse('login')
        assert len(mail.outbox) == 1
        assert 'Witamy na pokładzie!' in mail.outbox[0].subject

    def test_register_view_invalid(self, client, new_user_invalid, regular_users_group):
        # Test invalid registration shows correct response
        response = client.post(reverse('register'), data=new_user_invalid)

        assert response.status_code == 200

    def test_activate_success(self, client, regular_user):
        # Test successful account activation and email confirmation
        user = regular_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        response = client.get(reverse('activate', args=[uid, token]))

        assert response.status_code == 302
        assert 'Dziękujemy za potwierdzenie :) Twoje konto zostało zweryfikowane.' in [m.message for m in get_messages(response.wsgi_request)]
        user.refresh_from_db()
        assert user.profile.email_confirmed is True

    def test_activate_token_invalid(self, client, regular_user):
        # Test invalid activation token returns correct response
        user = regular_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = 'wrong-token'

        response = client.get(reverse('activate', args=[uid, invalid_token]))

        assert response.status_code == 302
        assert 'Link aktywacyjny jest nieprawidłowy!' in [m.message for m in get_messages(response.wsgi_request)]

    def test_password_reset_success(self, client, regular_user):
        # Test password reset with valid email shows correct response
        user = regular_user
        response = client.get(reverse('password_reset'), data={'email': 'user@example.com'})

        assert response.status_code == 200

    def test_password_reset_invalid_email(self, client, regular_user):
        # Test password reset with invalid email shows correct response
        user = regular_user
        response = client.post(reverse('password_reset'), data={'email': 'wrongemail@example.com'})

        assert response.status_code == 200
        assert 'Nie znaleziono użytkownika z tym adresem email.' in [m.message for m in get_messages(response.wsgi_request)]

    def test_password_reset_confirm_success(self, client, regular_user):
        # Test password reset confirmation with matching passwords updates password
        user = regular_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = client.post(reverse('password_reset_confirm', args=[uid, token]), data={
            'new_password1': 'newstrongpassword123',
            'new_password2': 'newstrongpassword123'
        })

        assert response.status_code == 302
        user.refresh_from_db()
        assert user.check_password('newstrongpassword123')

    def test_password_reset_confirm_mismatch(self, client, regular_user):
        # Test password reset confirmation with mismatching passwords shows correct response
        user = regular_user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = client.post(reverse('password_reset_confirm', args=[uid, token]), data={
            'new_password1': 'password123',
            'new_password2': 'differentpassword123'
        })

        assert response.status_code == 200


@pytest.mark.django_db
class TestContactViews:
    @pytest.fixture
    def url(self):
        return reverse('contact')

    @pytest.fixture
    def valid_form_data(self):
        return {
            'name': 'testuser',
            'email': 'test@example.com',
            'message': 'Test Message'
        }

chatbot_instance = get_chatbot()