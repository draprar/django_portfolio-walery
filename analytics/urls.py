from django.urls import path
from . import views

urlpatterns = [
    path("stats/", views.stats_view, name="stats"),
    path("overview/", views.overview_view, name="overview"),
    path("leave/", views.record_leave, name="record_leave"),
]
