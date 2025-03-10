from accounts.models import User
from branches.models import Branch
from calendars.models import CalendarThemeLesson,Calendar
from classes.models import (
    Class,StudentEnrolment,ClassLesson,StudentAttendance,
    EnrolmentExtension,ReplacementAttendance,VideoAssignment
)
from category.models import Category,ThemeLesson
from certificate.models import StudentCertificate
from feeStructure.models import Grade
from students.models import Students
from payments.models import InvoiceSequence,Invoice,Payment

from datetime import datetime ,timedelta,date
from django.db import connection
from django.db.models import Max
from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from django.db import connection

import json

class CustomError(Exception):

    def __init__(self, message :str , code:int):
        self.message = message
        self.code = code

    def __str__(self):
        return f"Error {self.code}: {self.message}"

class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        # max_number = InvoiceSequence.objects.filter(branch_id=1).aggregate(Max('number'))['number__max']

        grade = Grade.objects.get(id=2)

        balance = grade.price / 2
        print(grade.price)
        print(balance)

    def learn_select_related(self):
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

    def learn_prefetch_related(self):
        classes = Class.objects.prefetch_related("enrolments","enrolments__student").get(id=460)

        print(classes)

        for enrolment in classes.enrolments.all():
            print(enrolment.status)
            print(enrolment.remaining_lessons)
            print(enrolment.student.fullname)

        student_enrolments = StudentEnrolment.objects.select_related("student","classroom").get(id=5508)

        print(student_enrolments.remaining_lessons)
        print(student_enrolments.student.fullname)
        print(student_enrolments.classroom.name)
        print(student_enrolments.classroom.start_time)
        print(student_enrolments.classroom.end_time)
        print(student_enrolments.classroom.day)

        for query in connection.queries:
            print(query['sql'],end='\n\n')

    def _print_query(self):
        for query in connection.queries:
            print(query['sql'],end='\n\n')