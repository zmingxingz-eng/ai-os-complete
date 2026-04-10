from django.apps import AppConfig

class RbacConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.system.rbac"
    verbose_name = "RBAC 关系管理"
