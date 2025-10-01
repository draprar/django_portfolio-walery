import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

def custom_404_view(request, exception):
    logger.warning("404 Not Found: path=%s, ip=%s", request.path, request.META.get("REMOTE_ADDR"))
    return render(request, "404.html", status=404)