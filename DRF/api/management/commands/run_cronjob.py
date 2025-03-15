from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        print(f"Time now is {datetime.now()}")