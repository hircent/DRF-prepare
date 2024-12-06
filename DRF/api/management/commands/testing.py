from django.core.management.base import BaseCommand

from branches.models import Branch
from calendars.models import CalendarThemeLesson
from classes.models import Class,StudentEnrolment
from students.models import Students
import datetime
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        Students.objects.all().delete()