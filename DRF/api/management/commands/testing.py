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
        student = self.mapRefferalChannel(1)
        # current_kits = json.loads(student.starter_kits)
        print(student)
        # current_kits.append({"id": 20, "name": "Science Lab Kit - G5"})
        # student.starter_kits = current_kits
        # student.save()
        # print(student)

    def mapRefferalChannel(self,referral_channel):
        channel = {
            1:'Facebook',
            2:'Google Form',
            3:'Centre FB Page',
            4:'DeEmcee Referral',
            5:'External Referral',
            6:'Call In',
            7:'Others'
        }

        return channel.get(referral_channel)