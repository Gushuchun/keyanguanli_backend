from django.apps import AppConfig


class CompetitionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.competition"

    def ready(self):
        import apps.competition.siginal
        from .schedulers import start_scheduler
        start_scheduler()