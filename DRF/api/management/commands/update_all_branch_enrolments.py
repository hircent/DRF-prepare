from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from branches.models import Branch
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students


class Command(BaseCommand):
    help = 'Update all branch enrolments'

    def handle(self, *args, **kwargs):
        total_branch = Branch.objects.all().count()
        self._branch_enrolments(total_branch)

    def _branch_enrolments(self,total_branch):
        
        enrolments = StudentEnrolment.objects.filter(branch__id=9)

        self._update_enrolments(enrolments)

        # for i in range(total_branch):
        #     print("================================")
        #     print(f"Branch: {i+1}")
        #     enrolments = StudentEnrolment.objects.filter(branch__id=i+1)

        #     self._update_enrolments(enrolments)

    def _update_enrolments(self,enrolments):
        
        for e in enrolments:
            attendance_count = e.attendances.count()
            
            if e.status == 'IN_PROGRESS':
                print("================================")
                print(f"Remaining lessons before: {e.remaining_lessons}")
                print(f"Total attendances: {attendance_count}")
                print(f"Student's name: {e.student.fullname}")

                if attendance_count >= 24:
                    e.remaining_lessons = 0
                    e.is_active = False
                    e.status = 'COMPLETED'
                else:
                    e.remaining_lessons -= attendance_count

                print(f"Remaining lessons after: {e.remaining_lessons}")

            elif e.status == 'COMPLETED':
                e.remaining_lessons = 0
                e.is_active = False
            
            elif e.status == 'DROPPED_OUT':
                e.is_active = False

        # try:
        #     StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons','is_active','status'])
        #     print(f"Successfully updated for branch: {enrolments[0].branch.id}")
        # except:
        #     print(f"Failed to update for branch: {enrolments[0].branch.id}")