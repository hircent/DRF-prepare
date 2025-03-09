from .models import Payment, Invoice, InvoiceSequence
from django.db.models import Max
from django.db import transaction
from django.core.exceptions import ValidationError

from classes.models import StudentEnrolment

class PaymentService:

    @staticmethod
    @transaction.atomic
    def create_payment(enrolment, amount, parent,branch):
        try:
            new_invoice = PaymentService._create_invoice(branch)
            new_payment = Payment.objects.create(
                enrolment=enrolment,
                invoice=new_invoice,
                parent=parent,
                amount=amount,
                start_date=enrolment.start_date
            )
            return new_payment
        except Exception as e:
            raise ValidationError(f"Error creating payment: {str(e)}")

    @staticmethod
    def _create_invoice(branch):
        invoice_sequence = PaymentService._create_invoice_sequence(branch)
        new_invoice = Invoice.objects.create(invoice_sequence=invoice_sequence,branch=branch)
        return new_invoice

    @staticmethod
    def _create_invoice_sequence(branch):
        max_number = InvoiceSequence.objects.filter(branch=branch).aggregate(Max('number'))['number__max']

        if max_number is None:
            max_number = 0

        new_invoice_sequence = InvoiceSequence.objects.create(branch=branch,number=max_number+1)
        return new_invoice_sequence
    
    @staticmethod
    def delete_payment(enrolment_id):
        payments = Payment.objects.filter(enrolment_id=enrolment_id)
        
        for payment in payments:
            payment.status = 'VOIDED'
            payment.description = 'Enrolment deleted'
        
        Payment.objects.bulk_update(payments,['status','description'])
