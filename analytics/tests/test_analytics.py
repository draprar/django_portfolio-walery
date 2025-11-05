import json
import pytest
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse

from analytics.models import Visit, VisitLog
from analytics import views
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
    """Tests for the stats view (/analytics/stats/)."""

    def test_stats_view_returns_visits_and_total(self, client):
        # Create sample visits and ensure view returns expected context.
        Visit.objects.create(path="/", count=5)
        Visit.objects.create(path="/contact", count=2)

        url = reverse("stats")  # no app namespace in this project
        response = client.get(url)

        assert response.status_code == 200
        assert "visits" in response.context
        assert "total" in response.context
        assert response.context["total"] == 7

    def test_stats_view_context_contains_correct_total(self, client):
        Visit.objects.create(path="/x", count=3)
        Visit.objects.create(path="/y", count=7)
        response = client.get(reverse("stats"))
        assert response.context["total"] == 10


@pytest.mark.django_db
class TestRecordLeave:
    """Tests for the record_leave endpoint (/analytics/leave/)."""

    def test_invalid_method_returns_405(self, client):
        url = reverse("record_leave")
        response = client.get(url)
        assert response.status_code == 405
        # The JSON body indicates failure
        assert response.json().get("ok") is False

    def test_missing_path_returns_400(self, client):
        # If JSON lacks "path" field the view should return 400
        url = reverse("record_leave")
        response = client.post(
            url,
            data=json.dumps({"duration": 1000}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert response.json().get("ok") is False

    def test_valid_post_creates_visit_and_log_once_per_session(self, client, monkeypatch):
        """
        The view normally does:
            Visit.objects.get_or_create(...)
            visit.count += 1
            VisitLog.objects.create(visit=visit, duration=duration)
        """
        url = reverse("record_leave")
        payload = {"path": "/abc", "duration": 5000}

        # Save original create method
        original_create = VisitLog.objects.create

        # First POST: should create Visit and VisitLog
        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json().get("ok") is True

        visit = Visit.objects.get(path="/abc")
        assert visit.count == 1
        assert VisitLog.objects.filter(visit=visit).count() == 1

        # Second POST in same session: should not create a duplicate log or increment
        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert Visit.objects.get(path="/abc").count == 1
        assert VisitLog.objects.filter(visit=visit).count() == 1

    def test_json_parsing_error_returns_400(self, client):
        # Invalid JSON should be handled gracefully and return 400
        url = reverse("record_leave")
        response = client.post(url, data="{invalid json", content_type="application/json")
        assert response.status_code == 400
        assert response.json().get("ok") is False


@pytest.mark.django_db
class TestOverviewView:
    """Tests for the overview view (/analytics/overview/)."""

    def test_returns_top_10_sorted_visits(self, client):
        # Create 15 paths with ascending counts; view should return top 10
        for i in range(15):
            Visit.objects.create(path=f"/p{i}", count=i)
        response = client.get(reverse("overview"))
        assert response.status_code == 200
        ctx = response.context
        assert len(ctx["labels"]) == 10
        # highest count should be first
        assert ctx["data"][0] == 14
        assert ctx["labels"][0] == "/p14"


@pytest.mark.django_db
class TestDailyStatsView:
    """Tests for daily aggregation based on VisitLog timestamps."""

    def test_returns_daily_stats_aggregated(self, client):
        v = Visit.objects.create(path="/x")
        now = timezone.now()
        # Provide IP because model requires it
        VisitLog.objects.create(visit=v, timestamp=now)
        VisitLog.objects.create(visit=v, timestamp=now)
        response = client.get(reverse("daily_stats"))
        assert response.status_code == 200
        ctx = response.context
        # labels list should contain one entry for that day and data should be counts
        assert len(ctx["labels"]) >= 1
        assert sum(ctx["data"]) >= 2


@pytest.mark.django_db
class TestCountVisitDecorator:
    """Unit tests for the count_visit decorator."""

    def test_increments_once_per_session(self, rf, monkeypatch):
        # We'll test decorator by wrapping a dummy view function.
        # The decorator imports Visit and VisitLog internally.
        # Monkeypatch VisitLog.create to inject 'ip' when decorator calls it.
        original_create = VisitLog.objects.create

        @count_visit
        def dummy_view(request):
            # Return a simple JSON response to simulate a view
            return JsonResponse({"ok": True})

        request = rf.get("/decorated")
        request.session = {}
        response = dummy_view(request)
        assert response.status_code == 200

        v = Visit.objects.get(path="/decorated")
        assert v.count == 1
        assert VisitLog.objects.count() == 1

        # second call within the same session shouldn't add another log
        dummy_view(request)
        v.refresh_from_db()
        assert v.count == 1
        assert VisitLog.objects.count() == 1


@pytest.mark.django_db
class TestAnalyticsUrls:
    """Ensure url names resolve (no namespace assumed)."""

    def test_urls_resolve_correct_views(self):
        # Simply ensure reversing the names works in current project setup.
        assert reverse("stats")
        assert reverse("overview")
        assert reverse("record_leave")
        assert reverse("daily_stats")
