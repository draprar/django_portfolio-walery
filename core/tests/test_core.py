# core/tests/test_core.py
"""
Unit tests for the `core` app.
All tests are pure unit tests. No database access. All external dependencies are mocked.
"""

import json
from unittest.mock import Mock, patch
import pytest
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.test import RequestFactory


# ---------------------------------------------------------------------
# MODELS / VALIDATORS
# ---------------------------------------------------------------------
def test_validate_file_size_allows_5mb():
    from core.models import validate_file_size
    fake_file = Mock(size=5 * 1024 * 1024)
    validate_file_size(fake_file)


def test_validate_file_size_rejects_over_5mb():
    from core.models import validate_file_size
    fake_file = Mock(size=(5 * 1024 * 1024) + 1)
    with pytest.raises(ValidationError):
        validate_file_size(fake_file)


def test_project_str_returns_combined_titles():
    from core.models import Project
    p = Project(title_en="Hello", title_pl="Cześć")
    assert str(p) == "Hello / Cześć"


def test_file_extension_validator_rejects_bad_ext():
    from django.core.validators import FileExtensionValidator
    validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])
    fake_file = Mock()
    fake_file.name = "malicious.exe"
    with pytest.raises(ValidationError):
        validator(fake_file)


# ---------------------------------------------------------------------
# FORMS
# ---------------------------------------------------------------------
def test_contact_form_honeypot_blocks():
    from core.forms import ContactForm
    data = {"name": "Test", "email": "a@b.c", "message": "hi", "website": "spam"}
    form = ContactForm(data=data)
    assert not form.is_valid()
    assert "website" in form.errors


def test_contact_form_valid_calls_save(monkeypatch):
    """Ensure valid form calls model save()."""
    from core.forms import ContactForm
    from core import models

    monkeypatch.setattr(models.Contact, "save", lambda self, *a, **kw: None)

    data = {
        "name": "Tester",
        "email": "tester@example.com",
        "message": "Hello there, long enough message.",
        "website": "",
    }

    form = ContactForm(data=data)
    assert form.is_valid(), form.errors

    result = form.save()
    assert isinstance(result, models.Contact)


# ---------------------------------------------------------------------
# VIEWS
# ---------------------------------------------------------------------
def test_health_check_view_returns_ok():
    from core.views import health_check
    req = HttpRequest()
    resp = health_check(req)
    assert resp.status_code == 200
    assert json.loads(resp.content) == {"status": "ok"}


def test_homeview_get_uses_render_and_projects(monkeypatch):
    import core.views as views_mod

    fake_projects = [Mock(title_en="P1"), Mock(title_en="P2")]
    monkeypatch.setattr("core.views.Project", Mock(objects=Mock(all=Mock(return_value=fake_projects))))

    def fake_render(request, template_name, context):
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.context_data = context
        return fake_response

    monkeypatch.setattr("core.views.render", fake_render)

    resp = views_mod.HomeView().get(Mock())
    assert resp.status_code == 200
    assert "form" in resp.context_data
    assert "projects" in resp.context_data


def test_homeview_get_handles_database_error(monkeypatch):
    import core.views as views_mod

    from django.db import DatabaseError

    monkeypatch.setattr(
        "core.views.Project",
        Mock(objects=Mock(all=Mock(side_effect=DatabaseError("db down"))))
    )

    def fake_render(request, template_name, context):
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.context_data = context
        return fake_response

    monkeypatch.setattr("core.views.render", fake_render)

    resp = views_mod.HomeView().get(Mock())
    assert resp.status_code == 200
    assert resp.context_data["projects"] == []


def test_contactview_post_success_and_error_paths(monkeypatch):
    """Test success, email failure, and invalid form paths in ContactView.post."""
    import core.views as views_mod

    fake_request = Mock()
    fake_request.headers = {'x-requested-with': 'XMLHttpRequest'}
    fake_request.POST = {"name": "A", "email": "a@b.c", "message": "hello", "website": ""}

    # CASE 1: valid + email success
    mock_form = Mock()
    mock_form.is_valid.return_value = True
    mock_form.cleaned_data = {"name": "Tester", "email": "a@b.c", "message": "Hi!"}
    mock_form.save.return_value = Mock()
    monkeypatch.setattr("core.views.ContactForm", lambda *a, **k: mock_form)
    monkeypatch.setattr("core.views.send_brevo_email", lambda *a, **k: True)

    resp = views_mod.ContactView().post(fake_request)
    assert resp.status_code == 200
    assert json.loads(resp.content)["success"] is True

    # CASE 2: valid + email raises exception
    def raise_exc(*a, **k): raise Exception("smtp boom")
    monkeypatch.setattr("core.views.send_brevo_email", raise_exc)
    resp2 = views_mod.ContactView().post(fake_request)
    assert resp2.status_code == 500

    # CASE 3: invalid form
    bad_form = Mock()
    bad_form.is_valid.return_value = False
    bad_form.errors = {"email": ["invalid"]}
    monkeypatch.setattr("core.views.ContactForm", lambda *a, **k: bad_form)
    resp3 = views_mod.ContactView().post(fake_request)
    assert resp3.status_code == 400
    body3 = json.loads(resp3.content)
    assert "email" in body3["errors"]


def test_contactview_post_email_returns_none(monkeypatch):
    """When send_brevo_email returns falsy, view should return 500."""
    import core.views as views_mod

    fake_request = Mock()
    fake_request.headers = {'x-requested-with': 'XMLHttpRequest'}
    fake_request.POST = {}

    mock_form = Mock()
    mock_form.is_valid.return_value = True
    mock_form.cleaned_data = {"name": "X", "email": "x@x.x", "message": "m"}
    monkeypatch.setattr("core.views.ContactForm", lambda *a, **k: mock_form)
    monkeypatch.setattr("core.views.send_brevo_email", lambda *a, **k: None)

    resp = views_mod.ContactView().post(fake_request)
    assert resp.status_code == 500
    assert json.loads(resp.content)["success"] is False


def test_contactview_rejects_non_xhr(monkeypatch):
    import core.views as views_mod

    fake_request = Mock()
    fake_request.headers = {}
    fake_request.POST = {}
    resp = views_mod.ContactView().post(fake_request)
    assert resp.status_code == 400
    assert json.loads(resp.content)["success"] is False


def test_contactview_rejects_honeypot(monkeypatch):
    """Requests with a filled honeypot field should be rejected with 400."""
    import core.views as views_mod

    fake_request = Mock()
    fake_request.headers = {'x-requested-with': 'XMLHttpRequest'}
    fake_request.POST = {"website": "http://spam.example"}

    resp = views_mod.ContactView().post(fake_request)
    assert resp.status_code == 400
    assert json.loads(resp.content)["success"] is False


@pytest.mark.django_db
def test_contactview_get_returns_405(client):
    """GET on /contact/ must return 405 (only POST is allowed)."""
    from django.urls import reverse
    resp = client.get(reverse("contact"))
    assert resp.status_code == 405


# ---------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------
def test_send_brevo_email_success(monkeypatch):
    from core import email as email_mod

    class DummyConfig:
        def __init__(self):
            self.api_key = {}

    class DummyRestClient:
        def __init__(self):
            self.pool_manager = Mock(connection_pool_kw={})

    class DummyApiClient:
        def __init__(self, configuration):
            self.rest_client = DummyRestClient()

    class DummyApi:
        def send_transac_email(self, payload):
            return {"messageId": "ok"}

    def DummySendSmtpEmail(**kw):
        return {"payload": kw}

    dummy = Mock()
    dummy.Configuration = DummyConfig
    dummy.ApiClient = DummyApiClient
    dummy.TransactionalEmailsApi = lambda client: DummyApi()
    dummy.SendSmtpEmail = DummySendSmtpEmail

    monkeypatch.setattr(email_mod, "sib_api_v3_sdk", dummy)
    res = email_mod.send_brevo_email("subject", "<p>x</p>", ["a@b.c"])
    assert res == {"messageId": "ok"}


def test_send_brevo_email_handles_api_exception(monkeypatch):
    from core import email as email_mod

    class DummyConfig:
        def __init__(self):
            self.api_key = {}

    class DummyRestClient:
        def __init__(self):
            self.pool_manager = Mock(connection_pool_kw={})

    class DummyApiClient:
        def __init__(self, configuration):
            self.rest_client = DummyRestClient()

    class BrokenApi:
        def send_transac_email(self, payload):
            raise Exception("boom")

    dummy = Mock()
    dummy.Configuration = DummyConfig
    dummy.ApiClient = DummyApiClient
    dummy.TransactionalEmailsApi = lambda client: BrokenApi()
    dummy.SendSmtpEmail = lambda **kw: {"payload": kw}

    monkeypatch.setattr(email_mod, "sib_api_v3_sdk", dummy)
    res = email_mod.send_brevo_email("s", "<p>x</p>", ["a@b.c"])
    assert res is None


# ---------------------------------------------------------------------
# STORAGE
# ---------------------------------------------------------------------
def test_supabase_public_storage_url_reads_media_url(monkeypatch):
    from core.storages_backends import SupabasePublicStorage
    fake_settings = Mock()
    fake_settings.MEDIA_URL = "https://cdn.example/"
    monkeypatch.setattr("core.storages_backends.settings", fake_settings)
    inst = object.__new__(SupabasePublicStorage)
    assert inst.url("folder/file.jpg") == "https://cdn.example/folder/file.jpg"

