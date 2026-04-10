from django.contrib import admin
from .models import GroupProfile

@admin.register(GroupProfile)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "code", "description", "is_active", "created_at")
    search_fields = ("group__name", "code")
    list_filter = ("is_active",)
