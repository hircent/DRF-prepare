from django.db.models import Q,F ,Value
from branches.models import Branch
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from api.baseCommand import CustomBaseCommand
from django.db import transaction

class Command(CustomBaseCommand):
    help = 'Update remaining lesson'

    DEFAULT_LESSONS = 24
    EXTENDED_LESSONS = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("update_remaining_lessons",__name__)

    def handle(self, *args, **kwargs):
        enrolments = StudentEnrolment.objects.filter(is_active=True).prefetch_related(
            "extensions","attendances"
        )
        for e in enrolments:
            # attended_attendances = e.attendances.filter(status='ATTENDED')
            # absent_attendances = e.attendances.filter(status='ABSENT')
            frozen_attendances = e.attendances.filter(status='FREEZED')

            should_have_total_lessons = (
                self.DEFAULT_LESSONS + 
                (self.EXTENDED_LESSONS * e.extensions.count()) +
                frozen_attendances.count()
            )

            remaining_lessons = should_have_total_lessons - e.attendances.count()

            e.remaining_lessons = remaining_lessons

        StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons'])