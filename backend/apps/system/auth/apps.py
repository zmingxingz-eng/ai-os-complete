from django.apps import AppConfig

class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.system.auth"
    label = "system_auth"
    verbose_name = "认证鉴权"
