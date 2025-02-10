from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from branches.models import Branch
from calendars.models import CalendarThemeLesson,Calendar
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from accounts.models import User
from category.models import Category,ThemeLesson
from datetime import datetime ,timedelta,date
from django.db import connection
import json
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        ext = StudentAttendance.objects.filter(id=236460)

        print(ext)