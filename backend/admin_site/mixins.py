class AuditAdminMixin:
    readonly_fields = ("created_at", "updated_at", "creator", "updater")
