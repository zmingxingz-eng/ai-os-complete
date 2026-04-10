from apps.system.rbac.models import UserRole, RoleDataScope

class DataScopeFilter:
    @staticmethod
    def get_scope_type(user):
        if not user or not user.is_authenticated:
            return "self"
        role_ids = UserRole.objects.filter(user=user, is_active=True).values_list("role_id", flat=True)
        scopes = RoleDataScope.objects.filter(role_id__in=role_ids, is_active=True).select_related("organization")
        if not scopes.exists():
            return "self"
        if scopes.filter(scope_type="all").exists():
            return "all"
        if scopes.filter(scope_type="org_and_children").exists():
            return "org_and_children"
        if scopes.filter(scope_type="org").exists():
            return "org"
        return "self"

    @staticmethod
    def filter_queryset(queryset, user, user_field="creator", org_field=None):
        scope_type = DataScopeFilter.get_scope_type(user)
        if scope_type == "all":
            return queryset
        if scope_type == "self":
            return queryset.filter(**{user_field: user})
        if scope_type == "org" and org_field:
            organization = getattr(getattr(user, "profile", None), "organization", None)
            if organization:
                return queryset.filter(**{org_field: organization})
            return queryset.none()
        if scope_type == "org_and_children" and org_field:
            organization = getattr(getattr(user, "profile", None), "organization", None)
            if organization:
                return queryset.filter(**{f"{org_field}__id": organization.id})
            return queryset.none()
        return queryset.filter(**{user_field: user})
