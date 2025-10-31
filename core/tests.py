import io
import os
import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import activate
from unittest.mock import patch
from django.http import HttpRequest
from django.views.defaults import server_error

from core.models import Project, Contact, validate_file_size
from core.forms import ContactForm
from core.email import send_brevo_email


# --- Minimal required environment variables for runtime ---
# (These prevent import errors when services like AWS or Brevo are mocked.)
os.environ.setdefault("DJANGO_DEBUG", "True")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "dummy")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "dummy")
os.environ.setdefault("AWS_STORAGE_BUCKET_NAME", "dummy")
os.environ.setdefault("SUPABASE_PROJECT_REF", "dummy")
os.environ.setdefault("BREVO_API_KEY", "dummy")
os.environ.setdefault("DEFAULT_FROM_EMAIL", "test@example.com")


# --- MODELS ---
@pytest.mark.django_db
def test_project_str_and_ordering():
    """Ensure Project __str__ returns correct format and newest items come first."""
    p1 = Project.objects.create(title_en="A", title_pl="AA")
    p2 = Project.objects.create(title_en="B", title_pl="BB")
    assert str(p1) == "A / AA"
    assert list(Project.objects.all())[0] == p2  # newest first


@pytest.mark.django_db
def test_contact_str():
    """Ensure Contact __str__ includes the contact name."""
    c = Contact.objects.create(name="Jan", email="a@b.co", message="msg")
    assert "Jan" in str(c)


# --- FILE VALIDATION ---
def test_validate_file_size_raises():
    """Raise ValidationError when file exceeds 5 MB."""
    fake = io.BytesIO(b"x" * (6 * 1024 * 1024))  # 6 MB
    fake.size = len(fake.getvalue())
    with pytest.raises(ValidationError):
        validate_file_size(fake)


def test_validate_file_size_exact_limit_passes():
    """Allow file exactly at 5 MB limit."""
    fake = io.BytesIO(b"x" * (5 * 1024 * 1024))  # exactly 5 MB
    fake.size = len(fake.getvalue())
    validate_file_size(fake)  # should not raise


def test_validate_file_size_object_without_size():
    """Ensure graceful failure when object lacks .size attribute."""
    class Dummy:
        pass

    with pytest.raises(AttributeError):
        validate_file_size(Dummy())


# --- FORMS ---
@pytest.mark.django_db
def test_contact_form_valid_and_save():
    """Valid form should save and create a Contact record."""
    form = ContactForm(data={"name": "Jan", "email": "a@b.co", "message": "hi", "website": ""})
    assert form.is_valid()
    instance = form.save()
    assert Contact.objects.filter(pk=instance.pk).exists()


def test_contact_form_honeypot_detected():
    """Form with 'website' field filled should trigger honeypot detection."""
    form = ContactForm(data={"name": "Jan", "email": "a@b.co", "message": "hi", "website": "bot"})
    assert not form.is_valid()
    assert "Bot detected." in form.errors["website"][0]


def test_contact_form_missing_fields():
    """Form with missing required fields should be invalid."""
    form = ContactForm(data={})
    assert not form.is_valid()
    assert "name" in form.errors


# --- VIEWS ---
@pytest.mark.django_db
def test_health_check_view(client):
    """Health endpoint should return simple JSON response."""
    resp = client.get(reverse("health"))
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.django_db
def test_home_view_renders_template_and_context(client):
    """Home view should render with projects and contact form in context."""
    Project.objects.create(title_en="T", title_pl="T")
    resp = client.get(reverse("home"))
    assert resp.status_code == 200
    assert "projects" in resp.context
    assert "form" in resp.context
    templates = [t.name for t in resp.templates if t.name]
    assert any("core/" in t for t in templates)


@pytest.mark.django_db
@patch("core.views.send_brevo_email", return_value=True)
def test_contact_view_ajax_success(mock_email, client):
    """AJAX contact request should send email and return success JSON."""
    data = {"name": "Jan", "email": "a@b.co", "message": "hi", "website": ""}
    resp = client.post(reverse("contact"), data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    mock_email.assert_called_once()


@pytest.mark.django_db
def test_contact_view_no_xhr(client):
    """Non-AJAX requests should be rejected with 400."""
    data = {"name": "Jan", "email": "a@b.co", "message": "hi", "website": ""}
    resp = client.post(reverse("contact"), data)
    assert resp.status_code == 400
    assert not resp.json()["success"]


@pytest.mark.django_db
def test_contact_view_invalid_form(client):
    """Invalid AJAX form submission should return 400 with errors."""
    resp = client.post(reverse("contact"), {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert resp.status_code == 400
    assert resp.json()["success"] is False
    assert "errors" in resp.json()


@pytest.mark.django_db
@patch("core.views.send_brevo_email", return_value=None)
def test_contact_view_email_fail(mock_email, client):
    """Should return 500 when send_brevo_email returns None."""
    data = {"name": "Jan", "email": "a@b.co", "message": "hi", "website": ""}
    assert ContactForm(data).is_valid()
    resp = client.post(reverse("contact"), data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert resp.status_code == 500
    assert resp.json()["success"] is False


@pytest.mark.django_db
@patch("core.views.send_brevo_email", side_effect=Exception("fail"))
def test_contact_view_exception(mock_email, client):
    """Should return 500 when send_brevo_email raises an exception."""
    data = {"name": "Jan", "email": "a@b.co", "message": "hi", "website": ""}
    assert ContactForm(data).is_valid()
    resp = client.post(reverse("contact"), data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert resp.status_code == 500
    msg = resp.json().get("message", "").lower()
    assert "error" in msg or "an error" in msg


@pytest.mark.django_db
def test_custom_404_500_views(client, settings):
    """Ensure custom 404.html and 500.html templates exist and render properly."""
    resp_404 = client.get("/nonexistent-url/")
    assert resp_404.status_code == 404
    templates = [t.name for t in resp_404.templates if t.name]
    assert any("404" in t for t in templates)

    settings.DEBUG = False
    request = HttpRequest()
    resp_500 = server_error(request)
    assert resp_500.status_code == 500
    assert "500" in str(resp_500.content)


# --- EMAIL ---
def test_send_brevo_email_success(monkeypatch):
    """Simulate successful email sending through mocked API."""
    class DummyAPI:
        def send_transac_email(self, msg):
            return {"id": 123}

    monkeypatch.setattr("core.email.sib_api_v3_sdk.TransactionalEmailsApi", lambda client: DummyAPI())
    result = send_brevo_email("s", "<p>hi</p>", ["a@b.co"])
    assert result == {"id": 123}


def test_send_brevo_email_api_exception(monkeypatch):
    """Simulate API exception and ensure function returns None."""
    class DummyAPI:
        def send_transac_email(self, msg):
            raise Exception("API error")

    monkeypatch.setattr("core.email.sib_api_v3_sdk.TransactionalEmailsApi", lambda client: DummyAPI())
    result = send_brevo_email("s", "<p>hi</p>", ["a@b.co"])
    assert result is None


# --- TRANSLATIONS ---
@pytest.mark.django_db
def test_home_view_renders_in_polish(client):
    """Verify that activating Polish language renders localized content."""
    activate("pl")
    resp = client.get(reverse("home"))
    assert resp.status_code == 200
    html = resp.content.decode()
    assert any(word in html.lower() for word in ["projekt", "kontakt", "o mnie"])
