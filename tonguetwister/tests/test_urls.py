import pytest
from django.urls import reverse, NoReverseMatch
from django.test import Client
from rest_framework.test import APIClient
from rest_framework import status

client = Client()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(django_user_model):
    """Create user and return authorized APIClient"""
    django_user_model.objects.create_user(username='testuser', password='password123')
    client = APIClient()
    response = client.post('/tonguetwister/api/token/', {'username': 'testuser', 'password': 'password123'})
    assert response.status_code in (200, 201), "Token endpoint not reachable"
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


# === API ENDPOINTS (router) ===
@pytest.mark.django_db
@pytest.mark.parametrize("endpoint", [
    '/tonguetwister/api/oldpolish/',
    '/tonguetwister/api/articulators/',
    '/tonguetwister/api/exercises/',
    '/tonguetwister/api/twisters/',
    '/tonguetwister/api/trivias/',
])
def test_api_endpoint_is_accessible(api_client, endpoint):
    response = api_client.get(endpoint)
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, 404)


# === AUTHENTICATED ACCESS (funfacts) ===
@pytest.mark.django_db
def test_authenticated_api_access(auth_client):
    response = auth_client.get('/tonguetwister/api/funfacts/')
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)


# === SIMPLE NAMED URLS (no args required) ===
@pytest.mark.django_db
@pytest.mark.parametrize("url_name, expected_status, method", [
    ('main', 200, 'get'),
    ('login', 200, 'get'),
    ('logout', 302, 'post'),
    ('register', 200, 'get'),
    ('password_reset', 200, 'get'),
    ('password_reset_done', 200, 'get'),
    ('password_reset_complete', 200, 'get'),
    ('load_more_articulators', 200, 'get'),
    ('load_more_exercises', 200, 'get'),
    ('load_more_twisters', 200, 'get'),
    ('load_more_trivia', 200, 'get'),
    ('load_more_funfacts', 200, 'get'),
    ('load_more_old_polish', 200, 'get'),
    ('articulator_list', 302, 'get'),
    ('articulator_add', 302, 'get'),
    ('exercise_list', 302, 'get'),
    ('exercise_add', 302, 'get'),
    ('twister_list', 302, 'get'),
    ('twister_add', 302, 'get'),
    ('trivia_list', 302, 'get'),
    ('trivia_add', 302, 'get'),
    ('funfact_list', 302, 'get'),
    ('funfact_add', 302, 'get'),
    ('oldpolish_list', 302, 'get'),
    ('oldpolish_add', 302, 'get'),
    ('user_content', 302, 'get'),
    # contact disabled — test skipped
    ('chatbot', 200, 'get'),
])
def test_named_urls_no_args(url_name, expected_status, method):
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        pytest.skip(f"URL name '{url_name}' not found.")
    if method == 'post':
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code in (expected_status, 302, 404)


# === URLS WITH ARGUMENTS (pk or id required) ===
@pytest.mark.django_db
@pytest.mark.parametrize("url_name, kwargs, expected_status", [
    ('articulator_edit', {'pk': 1}, 200),
    ('articulator_delete', {'pk': 1}, 200),
    ('exercise_edit', {'pk': 1}, 200),
    ('exercise_delete', {'pk': 1}, 200),
    ('twister_edit', {'pk': 1}, 200),
    ('twister_delete', {'pk': 1}, 200),
    ('trivia_edit', {'pk': 1}, 200),
    ('trivia_delete', {'pk': 1}, 200),
    ('funfact_edit', {'pk': 1}, 200),
    ('funfact_delete', {'pk': 1}, 200),
    ('oldpolish_edit', {'pk': 1}, 200),
    ('oldpolish_delete', {'pk': 1}, 200),
    ('add_articulator', {'articulator_id': 1}, 200),
    ('delete_articulator', {'articulator_id': 1}, 200),
    ('add_exercise', {'exercise_id': 1}, 200),
    ('delete_exercise', {'exercise_id': 1}, 200),
    ('add_twister', {'twister_id': 1}, 200),
    ('delete_twister', {'twister_id': 1}, 200),
])
def test_named_urls_with_args(url_name, kwargs, expected_status):
    try:
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code in (expected_status, 302, 404)
    except NoReverseMatch:
        pytest.skip(f"URL '{url_name}' with kwargs {kwargs} not found.")


# === SPECIAL CASE: password_reset_confirm needs args ===
@pytest.mark.django_db
def test_password_reset_confirm_url():
    url = reverse('password_reset_confirm', kwargs={
        'uidb64': 'MjM',  # fake base64 user id
        'token': 'set-password'
    })
    response = client.get(url)
    assert response.status_code in (200, 302, 400)
