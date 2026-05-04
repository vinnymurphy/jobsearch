import os

from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# 2. Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys should
#   have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# 3. Load task modules from all registered Django apps.
app.autodiscover_tasks()
