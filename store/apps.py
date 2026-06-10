import os
import sys

from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = 'Книжный магазин'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
            return
        if any(cmd in sys.argv for cmd in ('migrate', 'makemigrations', 'seed_books', 'test', 'shell')):
            return
        from .scheduler import start_scheduler
        start_scheduler()
