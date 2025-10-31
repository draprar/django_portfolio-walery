import pytest
import tempfile
from django.test import override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from gallery.models import Category, Gallery
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestGalleryViews:
    """Tests for gallery app views"""

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_home_view(self, client):
        """Home view should render correctly and include context data"""
        category = Category.objects.create(title="Nature")
        gallery_item = Gallery.objects.create(category=category, image="images/test.jpg")

        response = client.get(reverse('gallery:gallery_home'))

        assert response.status_code == 200
        assert 'categories' in response.context
        assert 'selected_category' in response.context
        assert 'instagram_posts' in response.context
        assert gallery_item in response.context['object_list']

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_home_view_filtered_by_category(self, client):
        """Home view should filter gallery by selected category"""
        category = Category.objects.create(title="Nature")
        other_category = Category.objects.create(title="Animals")
        Gallery.objects.create(category=category, image="images/nature.jpg")
        Gallery.objects.create(category=other_category, image="images/animals.jpg")

        response = client.get(reverse('gallery:gallery_home') + '?category=Nature')

        assert response.status_code == 200
        assert len(response.context['object_list']) == 1
        assert response.context['object_list'][0].category.title == "Nature"

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_upload_image_view_get(self, client):
        """Admin should access upload image page"""
        user = User.objects.create_user(username='admin', password='password', is_staff=True)
        client.login(username='admin', password='password')

        response = client.get(reverse('gallery:upload-image'))

        assert response.status_code == 200
        assert 'form' in response.context

    @override_settings(SECURE_SSL_REDIRECT=False)
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_upload_image_view_post(self, client):
        """Admin should be able to upload image"""
        user = User.objects.create_user(username='admin', password='password', is_staff=True)
        category = Category.objects.create(title="Nature")
        client.login(username='admin', password='password')

        test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00"
            b"\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21"
            b"\xF9\x04\x01\x0A\x00\x01\x00\x2C\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C"
            b"\x01\x00\x3B",
            content_type="image/jpeg"
        )

        response = client.post(reverse('gallery:upload-image'), {
            'category': category.id,
            'image': test_image,
            'description': 'Test Image'
        })

        assert response.status_code == 302
        assert Gallery.objects.count() == 1
        uploaded_image = Gallery.objects.first()
        assert uploaded_image.image.name.startswith('images/test_image')

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_delete_image_view(self, client):
        """Admin should delete gallery image"""
        user = User.objects.create_user(username='admin', password='password', is_staff=True)
        category = Category.objects.create(title="Nature")
        gallery_item = Gallery.objects.create(category=category, image="images/test.jpg")
        client.login(username='admin', password='password')

        response = client.post(reverse('gallery:delete-image', args=[gallery_item.id]))

        assert response.status_code == 302
        assert Gallery.objects.count() == 0

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_create_category_view(self, client):
        """Admin should create new category"""
        user = User.objects.create_user(username='admin', password='password', is_staff=True)
        client.login(username='admin', password='password')

        response = client.post(reverse('gallery:create-category'), {'title': 'New Category'})

        assert response.status_code == 302
        assert Category.objects.count() == 1
        assert Category.objects.first().title == 'New Category'
