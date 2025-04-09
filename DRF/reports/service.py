from branches.models import Branch
from classes.models import StudentAttendance
from django.db.models import Q,Count,Sum
from django.db.models.query import QuerySet
from students.models import Students
from payments.models import Payment

class PaymentReportService:

    @staticmethod
    def get_royalty_fees(discounted_amount:int | float,branch:Branch) -> float:
        if(discounted_amount == 0):
            return 0
        percentage = branch.branch_grade.percentage
        return float(discounted_amount) * (percentage / 100)


    @staticmethod
    def get_student_statuses(country:str,branch_id:int | None = None) -> QuerySet[Students]:
        if branch_id:
            return Students.objects.filter(branch_id=branch_id).aggregate(
                total=Count('id'),
                in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
                dropped_out=Count('id', filter=Q(status='DROPPED_OUT')),
                graduated=Count('id', filter=Q(status='GRADUATED'))
            )
        
        return Students.objects.filter(branch__country__name=country).aggregate(
            total=Count('id'),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            dropped_out=Count('id', filter=Q(status='DROPPED_OUT')),
            graduated=Count('id', filter=Q(status='GRADUATED'))
        )

    @staticmethod
    def get_attendance_statuses(year: str, month: str, branch_id: int | None = None,country:str | None = None) -> QuerySet[StudentAttendance]:

        if branch_id:
            return StudentAttendance.objects.filter(
                branch_id=branch_id,date__year=year,date__month=month
            ).aggregate(
                absent=Count('id', filter=Q(status='ABSENT')),
                freeze=Count('id', filter=Q(status='FREEZED')),
                sfreezed=Count('id', filter=Q(status='SFREEZED')),
                replacement=Count('id', filter=Q(status='REPLACEMENT'))
            )
        
        return StudentAttendance.objects.filter(
                branch__country__name=country,date__year=year,date__month=month
            ).aggregate(
                absent=Count('id', filter=Q(status='ABSENT')),
                freeze=Count('id', filter=Q(status='FREEZED')),
                sfreezed=Count('id', filter=Q(status='SFREEZED')),
                replacement=Count('id', filter=Q(status='REPLACEMENT'))
            )
    
    @staticmethod
    def get_status_from_payment(year: str, month: str, branch_id: int | None = None,country:str | None = None):
        if branch_id:
            return Payment.objects.filter(
                start_date__year=year,start_date__month=month,enrolment__branch_id=branch_id
            ).aggregate(
                total_enrolment=Count('id', filter=Q(enrolment_type='ENROLMENT')),
                total_advance=Count('id', filter=Q(enrolment_type='ADVANCE')),
                total_early_advance=Count('id', filter=Q(enrolment_type='EARLY_ADVANCE')),
                total_extend=Count('id', filter=Q(enrolment_type='EXTEND')),
            )
        
        return Payment.objects.filter(
                start_date__year=year,start_date__month=month,enrolment__branch__country__name=country
            ).aggregate(
                total_enrolment=Count('id', filter=Q(enrolment_type='ENROLMENT')),
                total_advance=Count('id', filter=Q(enrolment_type='ADVANCE')),
                total_early_advance=Count('id', filter=Q(enrolment_type='EARLY_ADVANCE')),
                total_extend=Count('id', filter=Q(enrolment_type='EXTEND')),
            )

    @staticmethod
    def get_total_amount_of_the_month(branch_id:int,year:str, month:str) -> QuerySet[Payment]:
        payments =  Payment.objects.filter(
            start_date__year=year,start_date__month=month,enrolment__branch_id=branch_id
        ).aggregate(
            total_amount=Sum('amount'),
            total_discount=Sum('discount'),
            discounted_amount=Sum('amount') - Sum('discount') - Sum('early_advance_rebate'),
            early_advance_rebate=Sum('early_advance_rebate')
        )

        return (
            payments['total_amount'] if payments['total_amount'] else 0,
            payments['total_discount'] if payments['total_discount'] else 0,
            payments['early_advance_rebate'] if payments['early_advance_rebate'] else 0,
            payments['discounted_amount'] if payments['discounted_amount'] else 0
        )
    
    

    