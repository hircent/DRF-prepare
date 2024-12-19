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
        
        enrolments = StudentEnrolment.objects.filter(branch__id=2)

        self._update_enrolments(enrolments)

        # for i in range(total_branch):
        #     print("================================")
        #     print(f"Branch: {i+1}")
        #     enrolments = StudentEnrolment.objects.filter(branch__id=i+1)
        #     self._update_enrolments(enrolments)

    def _update_enrolments(self,enrolments):
        
        for e in enrolments:

            total_extension = EnrolmentExtension.objects.filter(enrolment=e).count()
            
            self._perform_update(e,total_extension)

        try:
            StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons','is_active','status'])
            print(f"Successfully updated for branch: {enrolments[0].branch.id}")
        except:
            print(f"Failed to update for branch: {enrolments[0].branch.id}")

    def _perform_update(self,enrolment,total_extension):

        freezed_count = enrolment.attendances.filter(status='FREEZED').count()
        attendances = enrolment.attendances.count()
        last_attendance_date = enrolment.attendances.last().date
        attendances_after_freeze = attendances - freezed_count
        remaining_lessons = enrolment.remaining_lessons

        print("================================")
        print(f"Branch: {enrolment.branch.id}")
        print(f"Student's name: {enrolment.student.fullname}")
        print(f"Remaining lessons: {remaining_lessons}")
        print(f"Attendances: {attendances}")
        print(f"Extension: {total_extension}")
        print(f"Last attendance date: {last_attendance_date}")
        print(f"Freezed_count: {freezed_count}")
        print(f"Attendances after freeze: {attendances_after_freeze}")

        # if enrolment.status == 'COMPLETED':
        #     enrolment.remaining_lessons = 0
        #     enrolment.is_active = False
        
        # elif enrolment.status == 'DROPPED_OUT':
        #     enrolment.is_active = False

        # elif enrolment.status == 'IN_PROGRESS':
            
        #     if attendances > enrolment.remaining_lessons:
        #         enrolment.remaining_lessons = 0
        #         enrolment.is_active = False
        #         enrolment.status = 'DROPPED_OUT'
        #     else:
        #         enrolment.remaining_lessons -= attendances

        #         if enrolment.remaining_lessons <= 0:
        #             enrolment.is_active = False
        #             enrolment.status = 'COMPLETED'

        # print(f"Remaining lessons now: {enrolment.remaining_lessons}")
