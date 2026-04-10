from django.contrib import admin
from .models import Menu

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "path", "component", "parent", "sort", "is_active", "created_at")
    search_fields = ("name", "path", "component")
    list_filter = ("is_active",)
