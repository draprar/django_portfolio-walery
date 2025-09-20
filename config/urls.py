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
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
