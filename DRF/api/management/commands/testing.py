from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from branches.models import Branch
from calendars.models import CalendarThemeLesson,Calendar
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension,ReplacementAttendance
from students.models import Students
from accounts.models import User
from category.models import Category,ThemeLesson
from datetime import datetime ,timedelta,date
from django.db import connection
import json
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        ext = ReplacementAttendance.objects.get(attendances_id=236454)

        print(ext)

    def learn(self):
        # Without select_related
        # This will make N+1 queries (1 for ReplacementAttendance, N for each related StudentAttendance)
        replacement = ReplacementAttendance.objects.all()
        for r in replacement:
            print(r.attendances.student.name)  # Makes a new query for each attendances access

        # With select_related
        # This makes only 1 query with JOINs
        replacement = ReplacementAttendance.objects.select_related('attendances', 'attendances__student')
        for r in replacement:
            print(r.attendances.student.name)  # No additional queries needed