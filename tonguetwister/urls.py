from django.contrib.auth.views import LogoutView
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import (OldPolishViewSet, ArticulatorViewSet, FunfactViewSet, ExerciseViewSet, TriviaViewSet,
                    TwisterViewSet, CustomTokenObtainPairView, HealthCheckView)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'oldpolish', OldPolishViewSet, basename='oldpolish')
router.register(r'articulators', ArticulatorViewSet, basename='articulators')
router.register(r'funfacts', FunfactViewSet, basename='funfacts')
router.register(r'exercises', ExerciseViewSet, basename='exercises')
router.register(r'twisters', TwisterViewSet, basename='twisters')
router.register(r'trivias', TriviaViewSet, basename='trivias')

urlpatterns = [
    path('', views.main, name='main'),
    path('content_management/', views.content_management, name='content_management'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('password_reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete_view, name='password_reset_complete'),
    path('load-more-articulators/', views.load_more_articulators, name='load_more_articulators'),
    path('load-more-exercises/', views.load_more_exercises, name='load_more_exercises'),
    path('load-more-twisters/', views.load_more_twisters, name='load_more_twisters'),
    path('load-more-trivia/', views.load_more_trivia, name='load_more_trivia'),
    path('load-more-funfacts/', views.load_more_funfacts, name='load_more_funfacts'),
    path('load-more-old-polish/', views.load_more_old_polish, name='load_more_old_polish'),
    path('articulators/', views.articulator_list, name='articulator_list'),
    path('articulators/add/', views.articulator_add, name='articulator_add'),
    path('articulators/<int:pk>/edit/', views.articulator_edit, name='articulator_edit'),
    path('articulators/<int:pk>/delete/', views.articulator_delete, name='articulator_delete'),
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/add/', views.exercise_add, name='exercise_add'),
    path('exercises/<int:pk>/edit/', views.exercise_edit, name='exercise_edit'),
    path('exercises/<int:pk>/delete/', views.exercise_delete, name='exercise_delete'),
    path('twisters/', views.twister_list, name='twister_list'),
    path('twisters/add/', views.twister_add, name='twister_add'),
    path('twisters/<int:pk>/edit/', views.twister_edit, name='twister_edit'),
    path('twisters/<int:pk>/delete/', views.twister_delete, name='twister_delete'),
    path('trivia/', views.trivia_list, name='trivia_list'),
    path('trivia/add/', views.trivia_add, name='trivia_add'),
    path('trivia/<int:pk>/edit/', views.trivia_edit, name='trivia_edit'),
    path('trivia/<int:pk>/delete/', views.trivia_delete, name='trivia_delete'),
    path('funfacts/', views.funfact_list, name='funfact_list'),
    path('funfacts/add/', views.funfact_add, name='funfact_add'),
    path('funfacts/<int:pk>/edit/', views.funfact_edit, name='funfact_edit'),
    path('funfacts/<int:pk>/delete/', views.funfact_delete, name='funfact_delete'),
    path('oldpolishs/', views.oldpolish_list, name='oldpolish_list'),
    path('oldpolishs/add/', views.oldpolish_add, name='oldpolish_add'),
    path('oldpolishs/<int:pk>/edit/', views.oldpolish_edit, name='oldpolish_edit'),
    path('oldpolishs/<int:pk>/delete/', views.oldpolish_delete, name='oldpolish_delete'),
    path('user-content/', views.user_content, name='user_content'),
    path('add-articulator/<int:articulator_id>/', views.add_articulator, name='add_articulator'),
    path('delete-articulator/<int:articulator_id>/', views.delete_articulator, name='delete_articulator'),
    path('add-exercise/<int:exercise_id>/', views.add_exercise, name='add_exercise'),
    path('delete-exercise/<int:exercise_id>/', views.delete_exercise, name='delete_exercise'),
    path('add-twister/<int:twister_id>/', views.add_twister, name='add_twister'),
    path('delete-twister/<int:twister_id>/', views.delete_twister, name='delete_twister'),
    path('contact/', views.contact, name='contact'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
]

# Serving media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
