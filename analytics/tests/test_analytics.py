import json
import pytest
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse

from analytics.models import Visit, VisitLog
from analytics.utils import count_visit


@pytest.mark.django_db
class TestAnalyticsModels:
    """Model-level tests for Visit and VisitLog."""

    def test_visit_str_returns_path_and_count(self):
        v = Visit.objects.create(path="/home", count=3)
        assert str(v) == "/home → 3"

    def test_visitlog_str_contains_path_and_timestamp(self):
        v = Visit.objects.create(path="/page")
        log = VisitLog.objects.create(visit=v)
        s = str(log)
        assert "/page" in s
        assert log.timestamp.strftime("%Y-%m-%d") in s


@pytest.mark.django_db
class TestStatsView:
    """Tests for the intentionally disabled stats view."""

    def test_stats_view_returns_empty_context_even_with_data(self, client):
        Visit.objects.create(path="/", count=5)
        Visit.objects.create(path="/contact", count=2)

        url = reverse("stats")
        response = client.get(url)

        assert response.status_code == 200
        assert "visits" in response.context
        assert "total" in response.context
        assert response.context["disabled"] is True
        assert response.context["total"] == 0
        assert list(response.context["visits"]) == []

    def test_stats_view_ignores_existing_rows(self, client):
        Visit.objects.create(path="/x", count=3)
        VisitLog.objects.create(visit=Visit.objects.get(path="/x"))
        response = client.get(reverse("stats"))
        assert response.context["total"] == 0
        assert list(response.context["visits"]) == []


@pytest.mark.django_db
class TestRecordLeave:
    """Tests for the inert leave endpoint."""

    def test_invalid_method_returns_405(self, client):
        url = reverse("record_leave")
        response = client.get(url)
        assert response.status_code == 405
        assert response.json().get("ok") is False

    def test_post_returns_disabled_and_creates_no_rows(self, client):
        url = reverse("record_leave")
        response = client.post(
            url,
            data=json.dumps({"path": "/abc", "duration": 1000}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {"ok": True, "disabled": True}
        assert Visit.objects.count() == 0
        assert VisitLog.objects.count() == 0

    def test_post_does_not_parse_or_validate_payload(self, client):
        url = reverse("record_leave")
        response = client.post(url, data="{invalid json", content_type="application/json")
        assert response.status_code == 200
        assert response.json() == {"ok": True, "disabled": True}
        assert Visit.objects.count() == 0
        assert VisitLog.objects.count() == 0


@pytest.mark.django_db
class TestOverviewView:
    """Tests for the intentionally disabled overview view."""

    def test_returns_empty_chart_even_with_existing_data(self, client):
        for i in range(15):
            Visit.objects.create(path=f"/p{i}", count=i)
        response = client.get(reverse("overview"))
        assert response.status_code == 200
        ctx = response.context
        assert ctx["disabled"] is True
        assert ctx["labels"] == []
        assert ctx["data"] == []


@pytest.mark.django_db
class TestDailyStatsView:
    """Tests for the intentionally disabled daily stats view."""

    def test_returns_empty_daily_stats_even_with_existing_logs(self, client):
        v = Visit.objects.create(path="/x")
        now = timezone.now()
        VisitLog.objects.create(visit=v, timestamp=now)
        VisitLog.objects.create(visit=v, timestamp=now)
        response = client.get(reverse("daily_stats"))
        assert response.status_code == 200
        ctx = response.context
        assert ctx["disabled"] is True
        assert ctx["labels"] == []
        assert ctx["data"] == []


@pytest.mark.django_db
class TestCountVisitDecorator:
    """Unit tests for the disabled count_visit decorator."""

    def test_preserves_view_and_does_not_write_to_db(self, rf):

        @count_visit
        def dummy_view(request):
            return JsonResponse({"ok": True})

        request = rf.get("/decorated")
        request.session = {}
        response = dummy_view(request)
        assert response.status_code == 200
        assert json.loads(response.content) == {"ok": True}
        assert Visit.objects.count() == 0
        assert VisitLog.objects.count() == 0


@pytest.mark.django_db
class TestAnalyticsUrls:
    """Ensure url names resolve (no namespace assumed)."""

    def test_urls_resolve_correct_views(self):
        # Simply ensure reversing the names works in current project setup.
        assert reverse("stats")
        assert reverse("overview")
        assert reverse("record_leave")
        assert reverse("daily_stats")
