from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from pathlib import Path

from students.models import Students
from classes.models import Class
from calendars.models import Calendar

class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        stu_start_date = datetime.strptime('2024-09-07','%Y-%m-%d')
        day = self.convertToDay(stu_start_date.weekday())
        print(f'Students starting from {stu_start_date.strftime("%Y-%m-%d")} on {day}')
      
        clas = Class.objects.filter(day=day)

        print(clas)

    def convertToDay(self,number):
        dic = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday',
        }   
        return dic[number]
    
    # def getAllStudents(self):
    #     return Students.objects.all()

    # def getStudentById(self,id):
    #     return Students.objects.get(id=id)

    # def getStudentByName(self,name):
    #     return Students.objects.filter(fullname=name)
    
    # def getClassById(self,id):
    #     return Class.objects.get(id=id)