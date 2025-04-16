from django.db.models import Q,F ,Value
from branches.models import Branch
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from api.baseCommand import CustomBaseCommand
from django.db import transaction

class Command(CustomBaseCommand):
    help = 'Update all branch enrolments'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("update_enrolments",__name__)

    def handle(self, *args, **kwargs):
        total_branch = Branch.objects.all().count()
        self._branch_enrolments(total_branch)

    def _branch_enrolments(self,total_branch):
        for i in range(total_branch):
            if i+1 == 26:
                continue
            enrolments = StudentEnrolment.objects.filter(branch__id=i+1)

            self._update_enrolments(enrolments)

    def _update_enrolments(self,enrolments):
        
        try:
            with transaction.atomic():
                for e in enrolments:
                    attendance_count = e.attendances.count()
                    
                    if e.status == 'IN_PROGRESS':

                        if attendance_count == e.remaining_lessons:
                            e.remaining_lessons = 0
                            e.is_active = False
                            e.status = 'COMPLETED'

                        elif attendance_count > e.remaining_lessons:
                            e.is_active = False
                            self.logger.error(
                                "Student %(name)s (Enrolment ID: %(id)d) "
                                "has attended more lessons (%(attended)d) "
                                "than remaining lessons (%(remaining)d).",
                                {
                                    "name": e.student.fullname,
                                    "id": e.id,
                                    "attended": attendance_count,
                                    "remaining": e.remaining_lessons
                                }
                            )
                        else:
                            e.remaining_lessons -= attendance_count

                    elif e.status == 'COMPLETED':
                        e.remaining_lessons = 0
                        e.is_active = False
                    
                    elif e.status == 'DROPPED_OUT':
                        e.is_active = False
                        
                StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons','is_active','status'])
                print(f"Successfully updated for branch: {enrolments[0].branch.id}")
                
        except Exception as e:
            self.logger.error(f"Failed to update for branch: {enrolments[0].branch.id}")
            self.logger.error(f"Something is wrong with enrolments: {e}")
            print(f"Failed to update for branch: {enrolments[0].branch.id}")
            raise Exception(f"Something is wrong with enrolments: {e}")
