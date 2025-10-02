from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin69/', admin.site.urls),
    path('', include('core.urls')),             # portfolio landing page
    path('gallery/', include('gallery.urls')),  # gallery
    path('rugby/', include('rugby.urls')),       # rugby
    path('tonguetwister/', include('tonguetwister.urls')),  # tonguetwister

    # API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/', include('core.urls')),
]

handler404 = "config.views.custom_404_view"

if settings.DEBUG:
    # serve static files in debug using static() only if needed
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # NOTE: we DO NOT serve MEDIA via Django static() because MEDIA is in Supabase.
