import sys
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        if "runserver" in sys.argv:
            from core import scheduler as sched

            sched.start()
