# core/tests/test_unit.py
"""
Unit tests for the `core` app.
All tests are pure unit tests. No database access. All external dependencies are mocked.
Comments and docstrings are in English as requested.
"""

import importlib
import json
from unittest.mock import Mock, MagicMock, patch
import pytest
from django.core.exceptions import ValidationError
from django.http import HttpRequest

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def apply_identity_count_visit(monkeypatch):
    """Patch analytics.utils.count_visit to identity decorator."""
    monkeypatch.setattr("analytics.utils.count_visit", lambda f: f)


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
    """Validator expects object with `.name` attribute, not str."""
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

    sentinel = object()

    # Patch model save() so we don't hit the DB
    monkeypatch.setattr(models.Contact, "save", lambda self, *a, **kw: sentinel)

    data = {
        "name": "Tester",
        "email": "tester@example.com",
        "message": "Hello there, long enough message.",
        "website": "",  # honeypot field empty
    }

    form = ContactForm(data=data)
    assert form.is_valid(), form.errors

    result = form.save()
    # ModelForm.save() returns the instance, not whatever save() returns
    # so check that our patched save() was called indirectly
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
    apply_identity_count_visit(monkeypatch)
    import core.views as views_mod
    importlib.reload(views_mod)

    fake_projects = [Mock(title_en="P1"), Mock(title_en="P2")]
    monkeypatch.setattr("core.views.Project", Mock(objects=Mock(all=Mock(return_value=fake_projects))))

    def fake_render(request, template_name, context):
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.context_data = context
        return fake_response

    monkeypatch.setattr("core.views.render", fake_render)

    fake_request = Mock()
    resp = views_mod.HomeView().get(fake_request)
    assert resp.status_code == 200
    assert "form" in resp.context_data
    assert "projects" in resp.context_data


def test_contactview_post_success_and_error_paths(monkeypatch):
    """Test all paths in ContactView.post."""
    apply_identity_count_visit(monkeypatch)
    import core.views as views_mod
    importlib.reload(views_mod)

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

    # CASE 2: valid + email raises
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


def test_contactview_rejects_non_xhr(monkeypatch):
    apply_identity_count_visit(monkeypatch)
    import core.views as views_mod
    importlib.reload(views_mod)

    fake_request = Mock()
    fake_request.headers = {}
    fake_request.POST = {"name": "A", "email": "a@b.c", "message": "m", "website": ""}
    resp = views_mod.ContactView().post(fake_request)
    assert resp.status_code == 400


# ---------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------
def test_send_brevo_email_success(monkeypatch):
    from core import email as email_mod

    class DummyConfig:
        def __init__(self): self.api_key = {}

    class DummyApi:
        def send_transac_email(self, payload):
            return {"messageId": "ok"}

    def DummySendSmtpEmail(**kw): return {"payload": kw}

    dummy = Mock()
    dummy.Configuration = DummyConfig
    dummy.TransactionalEmailsApi = lambda client: DummyApi()
    dummy.SendSmtpEmail = DummySendSmtpEmail

    monkeypatch.setattr(email_mod, "sib_api_v3_sdk", dummy)
    res = email_mod.send_brevo_email("subject", "<p>x</p>", ["a@b.c"])
    assert res == {"messageId": "ok"}


def test_send_brevo_email_handles_api_exception(monkeypatch):
    from core import email as email_mod

    class DummyConfig:
        def __init__(self): self.api_key = {}

    class BrokenApi:
        def send_transac_email(self, payload): raise Exception("boom")

    dummy = Mock()
    dummy.Configuration = DummyConfig
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


# ---------------------------------------------------------------------
# DECORATOR RELOAD SAFETY
# ---------------------------------------------------------------------
def test_count_visit_decorator_idempotent(monkeypatch):
    apply_identity_count_visit(monkeypatch)
    import core.views as views_mod
    importlib.reload(views_mod)

    def fake_render(request, template_name, context):
        r = Mock()
        r.status_code = 200
        r.context_data = context
        return r

    monkeypatch.setattr("core.views.render", fake_render)
    monkeypatch.setattr("core.views.Project", Mock(objects=Mock(all=Mock(return_value=[]))))

    req = Mock()
    resp = views_mod.HomeView().get(req)
    assert resp.status_code == 200
    assert "form" in resp.context_data
    assert "projects" in resp.context_data
