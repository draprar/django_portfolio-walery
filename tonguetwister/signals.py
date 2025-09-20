from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
        Signal to automatically create or update a user profile
        when a User instance is created or saved.
    """
    if created:
        # Create a new Profile instance for the newly created user
        Profile.objects.create(user=instance)
    # Ensure the existing or new Profile is saved/updated
    instance.profile.save()
