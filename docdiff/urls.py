from django.urls import path
from . import views
from analytics.utils import count_visit

app_name = "docdiff"

urlpatterns = [
    path("", count_visit(views.docdiff_view), name="index"),        # główny formularz uploadu
    path("compare/", views.docdiff_view, name="compare"),  # POST z plikami idzie tutaj
]
