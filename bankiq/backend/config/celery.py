"""Celery application instance for BankIQ async tasks."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("bankiq")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["tasks"])
