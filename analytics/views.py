from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Visit, VisitLog
import json


def stats_view(request):
    """Displays a list of all visits and the total number of entries."""
    visits = Visit.objects.all().order_by('-last_visit')
    total = sum(v.count for v in visits)
    return render(request, 'analytics/stats.html', {'visits': visits, 'total': total})


@csrf_exempt
def record_leave(request):
    """Records a unique visit within a session (IP-free, GDPR compliant)."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body.decode() or "{}")
        path = data.get("path")
        duration = float(data.get("duration", 0)) / 1000  # sekundy

        if not path:
            return JsonResponse({"ok": False, "error": "Missing path"}, status=400)

        # Unikalność w obrębie sesji
        session_key = f"visited_{path}"
        if not request.session.get(session_key, False):
            visit, _ = Visit.objects.get_or_create(path=path)
            visit.count += 1
            visit.save(update_fields=["count"])
            request.session[session_key] = True

            # Log tylko dla nowych sesji
            VisitLog.objects.create(visit=visit, duration=duration)

        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


def overview_view(request):
    """Prosty wykres 10 najczęściej odwiedzanych podstron."""
    visits = Visit.objects.all().order_by('-count')[:10]
    labels = [v.path for v in visits]
    data = [v.count for v in visits]
    return render(request, 'analytics/overview.html', {'labels': labels, 'data': data})


def daily_stats_view(request):
    """Daily statistics of all visits (based on VisitLog)."""
    daily = (
        VisitLog.objects
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(visits=Count("id"))
        .order_by("day")
    )

    labels = [entry["day"].strftime("%Y-%m-%d") for entry in daily]
    data = [entry["visits"] for entry in daily]

    return render(request, 'analytics/daily_stats.html', {'labels': labels, 'data': data})
