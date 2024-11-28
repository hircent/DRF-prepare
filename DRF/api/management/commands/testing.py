from django.core.management.base import BaseCommand

from branches.models import Branch
from calendars.models import CalendarThemeLesson
import datetime
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        date = datetime.datetime(2024,1,1).date()
        end_date = datetime.datetime(2024,1,1).date()

        print((end_date - date)+ datetime.timedelta(days=1))