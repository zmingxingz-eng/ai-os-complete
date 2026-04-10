from django.contrib import admin
from .models import MenuPermission

@admin.register(MenuPermission)
class MenuPermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "menu", "permission", "perm_type", "sort", "is_active", "created_at")
    search_fields = ("menu__name", "permission__name", "permission__codename", "description")
    list_filter = ("perm_type", "is_active")
