from django.db.models import Q,F ,Value
from branches.models import Branch
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students
from api.baseCommand import CustomBaseCommand
from django.db import transaction
from datetime import datetime,date,timedelta
from django.core.management.base import CommandError

from django.db.models.query import QuerySet
from typing import List

class Command(CustomBaseCommand):
    help = 'Delete Class Lessons and Student Lessons'

    DEFAULT_LESSONS = 24
    EXTENDED_LESSONS = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("delete_class_attendances",__name__)

    def add_arguments(self, parser):
        parser.add_argument('--branchId', type=int,required=True, help='Branch ID')
        parser.add_argument('--from_date', type=str,required=True, help='Holiday from date')
        parser.add_argument('--to_date', type=str,required=True, help='Holiday to date')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stderr.write(self.style.SUCCESS('*** Proccesing......'))
        try:

            from_date = kwargs['from_date']
            to_date = kwargs['to_date']
            branchId = kwargs['branchId']

            self._validate_branch(branchId)
            
            class_lessons = self._get_class_lessons(from_date,to_date,branchId)
            student_attendances = self._get_student_attendances(from_date,to_date,branchId)

            self._delete_classLessons(class_lessons,branchId)
            self._delete_student_attendances(student_attendances,branchId)

            enrolments = self._get_enrolments(branchId)

            if enrolments.exists():
                self._update_remaining_lessons(enrolments)
            else:
                self.logger.error(f"No Enrolments found for {branchId}")
                self.stderr.write(self.style.ERROR(f"No Enrolments found for {branchId}"))
            
        except Exception as e:
            self.logger.error(f"Error during delete_class_attendances: {str(e)}")
            self.stderr.write(self.style.ERROR(f"Error during delete_class_attendances: {str(e)}"))
            raise(f"Error during delete_class_attendances: {str(e)}")
        
        self.stderr.write(self.style.SUCCESS('*** Done!'))
        
    def _update_remaining_lessons(self,enrolments:QuerySet[StudentEnrolment]):
        enrolments = StudentEnrolment.objects.filter(branch_id=1).prefetch_related(
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
            status = 'IN_PROGRESS'
            is_active = True

            if remaining_lessons < 0:
                remaining_lessons = 0
                status = 'COMPLETED'
                is_active = False

            e.remaining_lessons = remaining_lessons
            e.status = status
            e.is_active = is_active

        StudentEnrolment.objects.bulk_update(enrolments,['remaining_lessons','status','is_active'])


    def _get_enrolments(self,branchId:int) -> QuerySet[StudentEnrolment]:
        enrolments = StudentEnrolment.objects.filter(branch_id=branchId).prefetch_related(
            "extensions","attendances"
        )
        return enrolments

    def _delete_classLessons(self,class_lessons:QuerySet[ClassLesson],branchId:int):
        if class_lessons.exists():
            class_lessons.delete()
            self.stdout.write(self.style.SUCCESS(f"Class Lessons deleted"))
        else:
            self.logger.error(f"No Class Lessons found for {branchId}")
            self.stdout.write(self.style.WARNING(f"No Class Lessons found for {branchId}"))

    def _delete_student_attendances(self,student_attendances:QuerySet[StudentAttendance],branchId:int):
        if student_attendances.exists():
            student_attendances.delete()
            self.stdout.write(self.style.SUCCESS(f"Student Attendances deleted"))
        else:
            self.logger.error(f"No Student Attendances found for {branchId}")
            self.stdout.write(self.style.WARNING(f"No Student Attendances found for {branchId}"))
        
        
    def _get_class_lessons(self,from_date:str,to_date:str,branch_id:int) -> QuerySet[ClassLesson]:
        return ClassLesson.objects.filter(
            branch_id=branch_id,
            date__gte=from_date,
            date__lte=to_date
        )

         

    def _get_student_attendances(self,from_date:str,to_date:str,branch_id:int) -> QuerySet[StudentAttendance]:
        return StudentAttendance.objects.filter(
            branch_id=branch_id,
            date__gte=from_date,
            date__lte=to_date
        )

        
    

    def _get_dates(self,from_date:str,to_date:str) -> List[str]:
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

        total_days = (to_date - from_date).days + 1

        date_arr = []
        for i in range(total_days):
            date = from_date + timedelta(days=i)
            date_arr.append(date.strftime("%Y-%m-%d"))

        return date_arr
    
    def _validate_branch(self,branch_id:int) -> None:
        branch = Branch.objects.filter(id=branch_id)

        if not branch.exists():
            self.logger.error(f"Branch {branch_id} does not exist")
            self.stderr.write(self.style.ERROR(f"Branch {branch_id} does not exist"))
            raise(f"Branch {branch_id} does not exist")
        
        self.stdout.write(self.style.SUCCESS(f"{branch[0].display_name} found! Continuing..."))