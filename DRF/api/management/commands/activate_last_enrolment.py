from django.db.models import Q,F ,Value
from branches.models import Branch
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from api.baseCommand import CustomBaseCommand
from django.db import transaction

class Command(CustomBaseCommand):
    help = 'Activate last enrolment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("activate last enrolment",__name__)

    def handle(self, *args, **kwargs):
        students = Students.objects.all().prefetch_related("enrolments")

        try:
            enrolments_to_update = []

            for student in students:
                enrolments = student.enrolments.all()

                if enrolments.exists():
                    first_enrolment = enrolments.first()
                    first_enrolment.is_active = True
                    enrolments_to_update.append(first_enrolment)

                if len(enrolments_to_update) > 500:
                    StudentEnrolment.objects.bulk_update(enrolments_to_update, ['is_active'])
                    enrolments_to_update = []
                    self.logger.info(f"Updated {len(enrolments_to_update)} enrolments")

            # Now bulk update all modified enrolments
            if enrolments_to_update:
                StudentEnrolment.objects.bulk_update(enrolments_to_update, ['is_active'])
                self.logger.info(f"Updated {len(enrolments_to_update)} enrolments")

        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            raise(f"Error: {str(e)}")
