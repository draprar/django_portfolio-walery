from functools import wraps
from django.utils import timezone
from datetime import timedelta
from .models import Visit, VisitLog

def get_client_ip(request):
    """Gets the user's IP, including reverse proxy."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def count_visit(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        path = request.path
        ip = get_client_ip(request)

        visit, _ = Visit.objects.get_or_create(path=path)
        now = timezone.now()
        window = now - timedelta(minutes=5)

        recent = visit.logs.filter(ip=ip, timestamp__gte=window).exists()
        if not recent:
            visit.count += 1
            visit.save()
            VisitLog.objects.create(visit=visit, ip=ip)

        return view_func(request, *args, **kwargs)
    return wrapper
