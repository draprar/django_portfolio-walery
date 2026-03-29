import logging

from django.db import DatabaseError

from .models import Category


logger = logging.getLogger(__name__)


def categories(request):
    # This context processor runs for most templates; avoid global 500 on DB hiccups.
    try:
        return {"categories": list(Category.objects.all())}
    except DatabaseError:
        logger.exception("Failed to load gallery categories in context processor")
        return {"categories": []}
