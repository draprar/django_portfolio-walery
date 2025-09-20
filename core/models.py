from django.db import models

class Project(models.Model):
    title_en = models.CharField(max_length=200)
    title_pl = models.CharField(max_length=200)
    desc_en = models.TextField(blank=True)
    desc_pl = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)

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