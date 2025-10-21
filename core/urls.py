from django.urls import path
from .views import HomeView, ContactView, health_check
from analytics.utils import count_visit

urlpatterns = [
    path('', count_visit(HomeView.as_view()), name='home'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('health/', health_check, name='health'),
]
