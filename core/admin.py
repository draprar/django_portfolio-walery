from django.contrib import admin
from django.utils.html import format_html
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_en", "title_pl", "github_url", "live_url", "created_at", "admin_image_preview")
    search_fields = ("title_en", "title_pl")
    readonly_fields = ("admin_image_preview",)

    def admin_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px; max-width:200px; object-fit:contain;"/>',
                obj.image.url
            )
        return "-"
    admin_image_preview.short_description = "Preview"