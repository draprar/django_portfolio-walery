from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_en", "title_pl", "github_url", "live_url", "created_at")
    search_fields = ("title_en", "title_pl")