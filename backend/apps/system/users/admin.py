from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "username", "full_name", "mobile", "organization", "email", "is_active", "is_staff")
    search_fields = ("username", "full_name", "mobile", "email")
    list_filter = ("is_active", "is_staff", "organization")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("基础信息", {"fields": ("full_name", "email", "mobile", "organization", "position_name")}),
        ("权限", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("重要时间", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "full_name", "email", "mobile", "organization", "position_name", "password1", "password2", "is_active", "is_staff"),
        }),
    )
