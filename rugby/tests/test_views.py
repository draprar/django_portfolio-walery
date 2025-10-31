from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from rugby.models import Post
import pytest


@pytest.mark.django_db
class TestPostListView:

    def setup_method(self):
        self.client = Client()

    def test_post_list_view_with_posts(self):
        user = User.objects.create(username="testuser")
        Post.objects.create(
            author=user,
            title="Test Post",
            text="This is a test post.",
            published_date=timezone.now(),
        )
        url = reverse("post_list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert "posts" in response.context
        assert len(response.context["posts"]) == 1

    def test_post_list_view_no_posts(self):
        url = reverse("post_list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert "posts" in response.context
        assert len(response.context["posts"]) == 0

    def test_post_list_only_published(self):
        user = User.objects.create(username="testuser")
        # Post z przyszłą datą, nie powinien się pokazać
        Post.objects.create(
            author=user,
            title="Future Post",
            text="Should not appear",
            published_date=timezone.now() + timezone.timedelta(days=1),
        )
        url = reverse("post_list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.context["posts"]) == 0
