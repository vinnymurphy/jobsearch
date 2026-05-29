from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"

    def ready(self):
        # We import the signals here to ensure they are registered
        # when the 'jobs' app is loaded into memory.
        import jobs.signals  # noqa: F401,E402,W0611
