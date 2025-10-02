from django.urls import path
from .views import HomeView, ContactView, health_check

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('health/', health_check, name='health'),
]
