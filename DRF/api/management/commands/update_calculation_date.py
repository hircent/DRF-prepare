from django.db.models import Q,F ,Value
from branches.models import Branch
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from api.baseCommand import CustomBaseCommand
from django.db import transaction

class Command(CustomBaseCommand):
    help = 'Update calculate date from start_date'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("update_calculate_date",__name__)

    @transaction.atomic
    def handle(self, *args, **kwargs):
        try:
           
            StudentEnrolment.objects.all().select_for_update().update(calculate_date=F('start_date'))

            print(f"Successfully updated for enrolments")

        except Exception as e:
            self.logger.error(f"Failed to update for enrolments")
