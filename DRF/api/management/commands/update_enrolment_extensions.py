from api.baseCommand import CustomBaseCommand
from api.mixins import BlockedDatesMixin
from classes.models import EnrolmentExtension, StudentEnrolment
from django.db import transaction
from datetime import datetime

class Command(CustomBaseCommand,BlockedDatesMixin):
    help = 'Update enrolment extension'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("update_enrolment_extension",__name__)

    def add_arguments(self, parser):
        today = datetime.now()
        parser.add_argument('--date', type=str, default=today.strftime("%Y-%m-%d"), help='Date to update enrolment extension')
    
    @transaction.atomic
    def handle(self, *args, **kwargs):
        try:
            request_date = kwargs['date']
            date = datetime.strptime(request_date, '%Y-%m-%d').date()

            exts = EnrolmentExtension.objects.filter(start_date=date,status='PENDING').select_related(
                "enrolment"
            )

            if exts.exists():
                enrolments = []
                for e in exts:
                    e.status = 'EXTENDED'
                    e.enrolment.remaining_lessons += 12
                    enrolments.append(e.enrolment)

                EnrolmentExtension.objects.bulk_update(exts,["status"])

                if enrolments:
                    self.update_enrolment_remaining_lesson(enrolments)
            else:
                self.logger.info(f"No enrolment extension to be operated for date :{str(date)}")

        except Exception as e:
            self.logger.warning(f"Enrolment extension operation failed on date:{str(date)}")
            self.logger.warning(f"Msg :{str(e)}")
            raise

    def update_enrolment_remaining_lesson(self,enrolments:list[StudentEnrolment]):

        StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons'])
