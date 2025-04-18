from .models import Payment, Invoice, InvoiceSequence
from django.db.models import Max
from django.db import transaction
from django.core.exceptions import ValidationError

from accounts.models import User
from branches.models import Branch
from classes.models import StudentEnrolment
from typing import List
from datetime import datetime

class PaymentService:

    @staticmethod
    @transaction.atomic
    def create_payment(enrolment:StudentEnrolment, 
                       amount:float, 
                       pre_outstanding:float, 
                       parent:User,
                       enrolment_type:str,
                       early_advance_rebate:float=0, 
                       description:str=None,
        ):

        try:
            new_payment = Payment.objects.create(
                enrolment=enrolment,
                parent=parent,
                amount=amount,
                early_advance_rebate=early_advance_rebate,
                pre_outstanding=pre_outstanding,
                start_date=enrolment.start_date,
                enrolment_type=enrolment_type,
                description=description
            )
            return new_payment
        except Exception as e:
            raise ValidationError(f"Error creating payment: {str(e)}")

    @staticmethod
    def get_pre_outstanding(enrolment:StudentEnrolment) -> float:

        payment = Payment.objects.filter(enrolment=enrolment,status='PAID')

        if payment.exists():
            return payment.last().post_outstanding
        
        return 0

    @staticmethod
    def create_invoice(branch:Branch) -> Invoice:
        invoice_sequence = PaymentService._create_invoice_sequence(branch)
        new_invoice = Invoice.objects.create(
            invoice_sequence=invoice_sequence,
            branch=branch,
            paid_at=datetime.today().date()
        )
        return new_invoice

    @staticmethod
    def _create_invoice_sequence(branch:Branch) -> InvoiceSequence:
        max_number = InvoiceSequence.objects.filter(branch=branch).aggregate(Max('number'))['number__max']

        if max_number is None:
            max_number = 0

        new_invoice_sequence = InvoiceSequence.objects.create(branch=branch,number=max_number+1)
        return new_invoice_sequence
    
    @staticmethod
    def void_payments(enrolment_ids:List[int],description:str) -> None:
        payments = Payment.objects.filter(enrolment_id__in=enrolment_ids)
        
        for payment in payments:
            payment.status = 'VOIDED'
            payment.description = description
        
        Payment.objects.bulk_update(payments,['status','description'])
