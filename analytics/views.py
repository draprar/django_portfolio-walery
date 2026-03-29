from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def stats_view(request):
    """Render an intentionally inert analytics dashboard."""
    return render(request, 'analytics/stats.html', {'visits': [], 'total': 0, 'disabled': True})


@csrf_exempt
def record_leave(request):
    """Analytics endpoint kept for compatibility, but tracking is disabled."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid method"}, status=405)

    return JsonResponse({"ok": True, "disabled": True})


def overview_view(request):
    """Render an empty overview because analytics is disabled."""
    return render(request, 'analytics/overview.html', {'labels': [], 'data': [], 'disabled': True})


def daily_stats_view(request):
    """Render empty daily stats because analytics is disabled."""
    return render(request, 'analytics/daily_stats.html', {'labels': [], 'data': [], 'disabled': True})
