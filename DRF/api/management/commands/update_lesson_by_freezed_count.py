from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from branches.models import Branch
from calendars.models import CalendarThemeLesson
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from accounts.models import User
from category.models import Category,ThemeLesson
import datetime
from django.db import connection
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        total_branch = Branch.objects.all().count()
        self._branch_enrolments(total_branch)

    def _branch_enrolments(self,total_branch):

        for i in range(total_branch):
            print("================================")
            print(f"Branch: {i+1}")
            enrolments = StudentEnrolment.objects.filter(branch__id=i+1)
            self._update_lesson_by_freezed_count(enrolments)

        
    def _update_lesson_by_freezed_count(self,enrolments):

        for enrolment in enrolments:
            freezed_count = enrolment.attendances.filter(status='FREEZED').count()
            enrolment.remaining_lessons += freezed_count
            
        try:
            StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons'])
            print(f"Successfully updated for branch: {enrolments[0].branch.id}")
        except:
            print('bulk update failed')