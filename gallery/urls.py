from django.urls import path

from analytics.utils import count_visit

from .views import CategoryListView, CreateCategory, DeleteImage, GalleryListView, Home, UploadImage

app_name = 'gallery'

urlpatterns = [
    path('', count_visit(Home.as_view()), name='gallery_home'),
    path('upload-image/', UploadImage.as_view(), name='upload-image'),
    path('delete-image/<int:pk>', DeleteImage.as_view(), name='delete-image'),
    path('create-category/', CreateCategory.as_view(), name='create-category'),
    #path('contact/', ContactView.as_view(), name='contact'),
    path('api/categories/', CategoryListView.as_view(), name='api-categories'),
    path('api/gallery/', GalleryListView.as_view(), name='api-gallery'),
]
