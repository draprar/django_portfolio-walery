from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Visit, VisitLog
import json

def stats_view(request):
    visits = Visit.objects.all().order_by('-last_visit')
    total = sum(v.count for v in visits)
    return render(request, 'analytics/stats.html', {'visits': visits, 'total': total})


@csrf_exempt
def record_leave(request):
    """Records the duration of the visit sent from JS (sendBeacon)."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode())
            path = data.get("path")
            duration = float(data.get("duration", 0)) / 1000  # sekundy
            ip = request.META.get("REMOTE_ADDR")

            visit = Visit.objects.filter(path=path).first()
            if visit:
                VisitLog.objects.create(visit=visit, ip=ip, duration=duration)
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)
    return JsonResponse({"ok": False, "error": "Invalid method"}, status=405)


def overview_view(request):
    """A simple dashboard with a graph of the most frequently visited subpages."""
    visits = Visit.objects.all().order_by('-count')[:10]
    labels = [v.path for v in visits]
    data = [v.count for v in visits]
    return render(request, 'analytics/overview.html', {'labels': labels, 'data': data})
