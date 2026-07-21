import sys

from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        if getattr(settings, "RUN_SCHEDULER", True) and "runserver" in sys.argv:
            from core import scheduler as sched

            sched.start()
