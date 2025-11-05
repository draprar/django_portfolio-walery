from functools import wraps
from .models import Visit, VisitLog


def count_visit(view_func):
    """
    A decorator that counts unique visits based on Django sessions.
    Each user within a session is counted only once for a given path.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        path = request.path
        visit, _ = Visit.objects.get_or_create(path=path)

        session_key = f"visited_{path}"
        if not request.session.get(session_key, False):
            visit.count += 1
            visit.save(update_fields=["count"])
            VisitLog.objects.create(visit=visit)
            request.session[session_key] = True

        return view_func(request, *args, **kwargs)

    return wrapper
