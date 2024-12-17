from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from branches.models import Branch
from calendars.models import CalendarThemeLesson
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance
from students.models import Students
from accounts.models import User
from category.models import Category,ThemeLesson
import datetime
from django.db import connection
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        enrolments = ClassLesson.objects.get(id=94550)

        # check if the enrolment is completed, bulk_update needed
        print(enrolments.attendances.all())

        # checkdate = datetime.date(2024,12,23)

        # today = datetime.date.today()

        # days = (checkdate - today).days

        # check_after_week = days % 7
        # print(check_after_week)
        


        # print(connection.queries)