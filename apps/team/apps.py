from django.apps import AppConfig


class TeamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.team"

    def ready(self):
        import apps.team.siginal
        from .schedulers import start_scheduler
        start_scheduler()