from django.utils import timezone
from django.contrib.auth.models import User
from rugby.models import Post
import pytest


@pytest.mark.django_db
class TestPostModel:

    def test_create_post(self):
        user = User.objects.create(username="testuser")
        post = Post.objects.create(
            author=user,
            title="Test Post",
            text="This is a test post.",
            created_date=timezone.now(),
        )
        assert post.title == "Test Post"
        assert post.text == "This is a test post."
        assert post.published_date is None
        assert str(post) == "Test Post"

    def test_publish_post(self):
        user = User.objects.create(username="testuser")
        post = Post.objects.create(
            author=user,
            title="Publish Test Post",
            text="Publishing test post.",
            created_date=timezone.now(),
        )
        post.publish()
        assert post.published_date is not None
        assert post.published_date <= timezone.now()

    def test_delete_user_cascades_posts(self):
        user = User.objects.create(username="testuser")
        Post.objects.create(
            author=user,
            title="Test Post",
            text="This is a test post.",
            created_date=timezone.now(),
        )
        user.delete()
        assert Post.objects.count() == 0
