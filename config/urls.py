from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin69/', admin.site.urls),
    path('', include('core.urls')),             # portfolio landing page
    path('gallery/', include('gallery.urls')),  # gallery
    path('rugby/', include('rugby.urls')),       # rugby
    path('tonguetwister/', include('tonguetwister.urls'))  # rugby
]

if settings.DEBUG:
    # serve static files in debug using static() only if needed
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # NOTE: we DO NOT serve MEDIA via Django static() because MEDIA is in Supabase.
