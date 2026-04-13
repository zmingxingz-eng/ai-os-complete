from django.contrib import admin

from .models import Organization, Position, UserOrganizationRelation


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "org_kind",
        "parent",
        "leader",
        "is_temporary",
        "status",
        "sort",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "code", "path_name")
    list_filter = ("org_kind", "is_temporary", "status", "is_active")


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "category", "status", "sort", "is_active", "created_at")
    search_fields = ("name", "code", "category")
    list_filter = ("status", "is_active")


@admin.register(UserOrganizationRelation)
class UserOrganizationRelationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "organization", "position", "relation_type", "status", "created_at")
    search_fields = ("user__username", "user__full_name", "organization__name", "position__name")
    list_filter = ("relation_type", "status")
