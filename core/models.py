from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_file_size(file):
    max_mb = 5  # maksymalny rozmiar w MB — zmień jeśli chcesz
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(_(f"Max file size is {max_mb} MB"))

class Project(models.Model):
    title_en = models.CharField(max_length=200)
    title_pl = models.CharField(max_length=200)
    desc_en = models.TextField(blank=True)
    desc_pl = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(
        upload_to="projects/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size
        ],
        help_text="Allowed: jpg, png, gif, webp. Max 5 MB."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title_en} / {self.title_pl}"

class Contact(models.Model):
    """
    Represents a contact form submission from the portfolio page.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"