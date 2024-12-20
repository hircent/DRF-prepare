from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from branches.models import Branch
from calendars.models import CalendarThemeLesson
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from accounts.models import User
from category.models import Category,ThemeLesson
import datetime
from django.db import connection,transaction
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        total_branch = Branch.objects.all().count()
        self._branch_enrolments(total_branch)

    def _branch_enrolments(self,total_branch):
        enrolments = StudentEnrolment.objects.filter(branch__id=32)
        self._update_lesson_by_freezed_count(enrolments)

        # try:
        #     with transaction.atomic():
        #         for i in range(total_branch):
        #             print("================================")
        #             print(f"Branch: {i+1}")
        #             enrolments = StudentEnrolment.objects.filter(branch__id=i+1)
        #             self._update_lesson_by_freezed_count(enrolments)

        # except Exception as e:
        #     print(f"Error: {e}")

        
    def _update_lesson_by_freezed_count(self,enrolments):

        for enrolment in enrolments:
            freezed_count = enrolment.attendances.filter(status='FREEZED').count()
            print("=================================")
            print(f"Student name: {enrolment.student.fullname}")
            print(f"Enrolement ID: {enrolment.id}")
            print(f"Freezed lesson: {freezed_count}")
            enrolment.remaining_lessons += freezed_count
            
        try:
            StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons'])
            print(f"Successfully updated for branch: {enrolments[0].branch.id}")
        except:
            raise Exception("Error in updating enrolments")