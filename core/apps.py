import sys

from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        if "runserver" not in sys.argv:
            return

        # Desktop/hybrid have no separate build/deploy step to run `migrate`
        # (cloud does this in build.sh), so bring the DB up to date here,
        # before the server starts accepting requests. Two independently
        # idempotent steps — schema migration, then reference-data init —
        # never seed inside a migration.
        if settings.IS_LOCAL_MODE:
            from django.core.management import call_command

            call_command("migrate", interactive=False)
            call_command("setup_infrastructure")

        if getattr(settings, "RUN_SCHEDULER", True):
            from core import scheduler as sched

            sched.start()
