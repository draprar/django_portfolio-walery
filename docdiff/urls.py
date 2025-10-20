from django.urls import path
from . import views

app_name = "docdiff"

urlpatterns = [
    path("", views.docdiff_view, name="index"),        # główny formularz uploadu
    path("compare/", views.docdiff_view, name="compare"),  # POST z plikami idzie tutaj
]
