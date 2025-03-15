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

from typing import List

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
        yesterday = datetime.now() - timedelta(days=1)
        day = yesterday.strftime("%A")
        
        all_branches = list(Branch.objects.all().values_list('id',flat=True))
        branch_id = 3
        # for branch_id in all_branches:
        has_lessons = self._is_class_lesson_exists(yesterday,branch_id)
        
        print(f"Branch ID: {branch_id} has lessons: {has_lessons}")

        if not has_lessons:
            self._create_class_lesson(yesterday,branch_id)

  
        class_lessons = self._get_class_lessons(yesterday,branch_id)

        for cl in class_lessons:
            class_instance = cl.class_instance
            enrolments = cl.class_instance.enrolments.filter(is_active=True)
            replacement_students = cl.class_instance.replacement_attendances.filter(
                date=yesterday
            ).select_related(
                'attendances','attendances__enrollment__student','attendances__enrollment'
            )
            print("==================================")
            print(f"Total enrolments: {enrolments.count()}")
            print(f"Lesson Time: {cl.class_instance.start_time} - {cl.class_instance.end_time}")
            self._create_attendances(yesterday,branch_id,enrolments,class_instance,cl.id)

            if replacement_students:
                self._update_replacement(replacement_students,branch_id)

    def _create_class_lesson(self,date:date,branch_id:int):

        class_instances = self._get_class_instance_by_day(date,branch_id)

        class_lessons_arr = []

        for ci in class_instances:
            class_lesson = ClassLesson(
                branch_id=branch_id,
                date=date,
                class_instance=ci
            )
            class_lessons_arr.append(class_lesson)

        if class_lessons_arr:
            ClassLesson.objects.bulk_create(class_lessons_arr)


    def _get_class_instance_by_day(self,date:date,branch_id:int) -> List[Class]:
        return Class.objects.filter(branch_id=branch_id,day=date.strftime("%A"))

    def _update_replacement(self,replacement_students:List[ReplacementAttendance],branch_id:int):

        for replacement in replacement_students:
            print("...........................")
            print(f"Id: {replacement.id}")
            print(f"Status: {replacement.status}")
            replacement.status = "ATTENDED"
            replacement.attendances.enrollment.remaining_lessons -= 1
            replacement.attendances.enrollment.save()
        ReplacementAttendance.objects.bulk_update(replacement_students,["status"])
        self.stdout.write(self.style.SUCCESS(f"Replacement attendances has been updated for branch id {branch_id}"))


    def _is_class_lesson_exists(self,date:date,branch_id:int) -> bool:
        return ClassLesson.objects.filter(branch_id=branch_id,date=date).exists()
    
    def _get_class_lessons(self,date:date,branch_id:int) -> List[ClassLesson]:
        return ClassLesson.objects.filter(branch_id=branch_id,date=date).select_related(
            "class_instance")
    
    def _create_attendances(self,date:date,branch_id:int,enrolments:List[StudentEnrolment],class_instance:Class,class_lesson_id:int):
        att_arr = []
        for en in enrolments:
            enrolment_id = en.id
            print("........................................")
            print(f"Remaining lessons: {en.remaining_lessons}")
            print(f"Student: {en.student.fullname}")
            print(f"Class: {class_instance.name}")
            print(f"Date: {date}")
            print(f"Day: {date.strftime('%A')}")

            is_attendance_exists = self._is_attendance_exists(date,branch_id,enrolment_id)

            if not is_attendance_exists:
                print("Attendance does not exist")
                st = StudentAttendance(
                    enrollment_id=enrolment_id,
                    branch_id=branch_id,
                    class_lesson_id=class_lesson_id,
                    date=date,
                    day=date.strftime("%A"),
                    start_time=class_instance.start_time,
                    end_time=class_instance.end_time,
                    has_attended=True,
                    status="ATTENDED"
                )
                att_arr.append(st)
                en.remaining_lessons -= 1
                en.save()

        if att_arr:
            StudentAttendance.objects.bulk_create(att_arr)
    
    def _is_attendance_exists(self,date:date,branch_id:int,enrollment_id:int) -> bool:
        return StudentAttendance.objects.filter(branch_id=branch_id,date=date,enrollment_id=enrollment_id).exists()

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