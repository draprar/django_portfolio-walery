from django.urls import path
from . import views
from analytics.utils import count_visit

urlpatterns = [
    path('', count_visit(views.post_list), name='post_list'),
]