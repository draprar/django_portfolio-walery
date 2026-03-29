from unittest.mock import Mock

from django.db import DatabaseError

from gallery.context_processors import categories


def test_categories_context_processor_returns_categories(monkeypatch):
    fake_categories = [Mock(title="A"), Mock(title="B")]
    monkeypatch.setattr(
        "gallery.context_processors.Category",
        Mock(objects=Mock(all=Mock(return_value=fake_categories))),
    )

    ctx = categories(Mock())
    assert ctx["categories"] == fake_categories


def test_categories_context_processor_handles_database_error(monkeypatch):
    monkeypatch.setattr(
        "gallery.context_processors.Category",
        Mock(objects=Mock(all=Mock(side_effect=DatabaseError("db down")))),
    )

    ctx = categories(Mock())
    assert ctx["categories"] == []


