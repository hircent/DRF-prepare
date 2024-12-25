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
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        today = date.today()
        parsed_date = date(2024,12,28)

        days = (parsed_date - today).days

        check_after_week = days // 7
        print(check_after_week)

    def _get_blocked_date(self,branch_id,year):
        all_events = Calendar.objects.filter(branch_id=2,year=2024)

        blockedDate = []

        for event in all_events:
            
            start_date = event.start_datetime.date()
            end_date = event.end_datetime.date()

            if start_date == end_date:
                blockedDate.append(start_date)
            else:

                while start_date <= end_date:
                    blockedDate.append(start_date)
                    start_date += timedelta(days=1)

        return blockedDate
