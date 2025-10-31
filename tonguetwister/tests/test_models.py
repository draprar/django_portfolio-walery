import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tonguetwister.models import (
    Profile, Twister, Articulator, Exercise, Trivia, Funfact,
    OldPolish, UserProfileTwister, UserProfileArticulator, UserProfileExercise
)


@pytest.mark.django_db
@pytest.mark.parametrize("model_class, text", [
    # Test string representation of Twister, Articulator, Exercise, Trivia, Funfact
    (Twister, "Test Twister"),
    (Articulator, "Test Articulator"),
    (Exercise, "Test Exercise"),
    (Trivia, "Test Trivia"),
    (Funfact, "Test Funfact")
])
def test_model_str(model_class, text):
    instance = model_class.objects.create(text=text)
    assert str(instance) == text


@pytest.mark.django_db
def test_oldpolish_str():
    # Test string representation of OldPolish instance
    old_polish = OldPolish.objects.create(old_text="staropolskie", new_text="nowomowa")
    expected_str = "Czy wiesz, że staropolskie staropolskie można przetłumaczyć jako nowomowa?"
    assert str(old_polish) == expected_str


@pytest.mark.django_db
def test_profile():
    # Test profile creation, string representation, and login streak update
    user = User.objects.create_user(username="testuser", password="test_password")
    profile, created = Profile.objects.get_or_create(user=user)
    assert str(profile) == "testuser Profile"

    profile.last_login_date = timezone.now().date() - timedelta(days=1)
    profile.save()
    profile.update_login_streak()
    assert profile.login_streak == 1


@pytest.mark.django_db
@pytest.mark.parametrize("model_class, related_field, user_profile_model_class", [
    # Test relationships between UserProfile models and their related fields
    (Twister, "twister", UserProfileTwister),
    (Articulator, "articulator", UserProfileArticulator),
    (Exercise, "exercise", UserProfileExercise),
])
def test_user_profile_relationship(model_class, related_field, user_profile_model_class):
    user = User.objects.create_user(username="testuser", password="test_password")
    related_instance = model_class.objects.create(text=f"Sample {model_class}.__name__")

    user_profile_model = user_profile_model_class.objects.create(user=user, **{related_field: related_instance})
    assert getattr(user_profile_model, related_field) == related_instance
