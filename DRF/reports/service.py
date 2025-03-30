from classes.models import StudentAttendance
from django.db.models import Q,Count,Sum
from django.db.models.query import QuerySet
from students.models import Students
from payments.models import Payment

class PaymentReportService:

    @staticmethod
    def get_student_statuses(branch_id:int) -> QuerySet[Students]:
        return Students.objects.filter(branch_id=branch_id).aggregate(
            total=Count('id'),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            dropped_out=Count('id', filter=Q(status='DROPPED_OUT')),
            graduated=Count('id', filter=Q(status='GRADUATED'))
        )

    @staticmethod
    def get_attendance_statuses(branch_id:int,year:str, month:str) -> QuerySet[StudentAttendance]:
        return StudentAttendance.objects.filter(
            branch_id=branch_id,date__year=year,date__month=month
        ).aggregate(
            absent=Count('id', filter=Q(status='ABSENT')),
            freeze=Count('id', filter=Q(status='FREEZED')),
            sfreezed=Count('id', filter=Q(status='SFREEZED')),
            replacement=Count('id', filter=Q(status='REPLACEMENT'))
        )

    @staticmethod
    def get_total_amount_of_the_month(branch_id:int,year:str, month:str) -> QuerySet[Payment]:
        payments =  Payment.objects.filter(
            start_date__year=year,start_date__month=month,enrolment__branch_id=branch_id
        ).aggregate(
            total_amount=Sum('amount'),
            total_discount=Sum('discount'),
            discounted_amount=Sum('amount') - Sum('discount'),
        )

        return (payments['total_amount'],payments['total_discount'],payments['discounted_amount'])
    
    

    