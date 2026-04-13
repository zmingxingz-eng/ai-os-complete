from django.apps import AppConfig
from django.db.backends.signals import connection_created

class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        def configure_sqlite(sender, connection, **kwargs):
            if connection.vendor != "sqlite":
                return
            raw_connection = connection.connection
            if raw_connection is None:
                return
            raw_connection.execute("PRAGMA journal_mode=OFF;")
            raw_connection.execute("PRAGMA synchronous=OFF;")

        connection_created.connect(configure_sqlite, dispatch_uid="common.configure_sqlite")
