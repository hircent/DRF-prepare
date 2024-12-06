from django.core.management.base import BaseCommand

from branches.models import Branch
from calendars.models import CalendarThemeLesson
from classes.models import Class
import datetime
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        Class.objects.all().delete()