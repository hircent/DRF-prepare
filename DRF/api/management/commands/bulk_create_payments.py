from api.baseCommand import CustomBaseCommand
from classes.models import EnrolmentExtension
from payments.models import Payment,Invoice
from branches.models import Branch
from classes.models import StudentEnrolment
from accounts.models import User
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import Payment'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_payments",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("payments.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    payment_arr = []
                    total_imported = 0

                    for row in reader:

                        if row['payment_invoice_id'] == '0':
                            continue

                        try:
                            StudentEnrolment.objects.get(id=row['payable_id'])
                            Invoice.objects.get(id=row['payment_invoice_id'])
                            User.objects.get(id=row['parent_id'])

                        except (StudentEnrolment.DoesNotExist,Invoice.DoesNotExist,User.DoesNotExist) as e:
                            if isinstance(e, StudentEnrolment.DoesNotExist):
                                self.logger.error(f"Student enrolment with id {row['payable_id']} does not exist in the database.")
                                continue
                            if isinstance(e, Invoice.DoesNotExist):
                                self.logger.error(f"Invoice with id {row['payment_invoice_id']} does not exist in the database.")
                                raise ImportError(f"Error while importing payments: {str(e)} {row}")
                            if isinstance(e, User.DoesNotExist):
                                self.logger.error(f"User with id {row['parent_id']} does not exist in the database.")
                                raise ImportError(f"Error while importing payments: {str(e)} {row}")

                        payment = Payment(
                            enrolment_id = row['payable_id'],
                            invoice_id = row['payment_invoice_id'],
                            parent_id = row['parent_id'],
                            amount = row['amount'],
                            discount = row['discount'],
                            paid_amount = row['paid_amount'],
                            start_date = self.parse_date(row['start_date']),
                            status = self._get_status(row['status']),
                            enrolment_type = self._get_enrolment_type(row['description']),
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at']),
                            pre_outstanding = row['pre_outstanding'],
                            post_outstanding = row['post_outstanding']
                        )

                        payment_arr.append(payment)

                        self.stdout.write(self.style.SUCCESS(f"Payments with id:{row['id']} has appended at time {datetime.now()}"))

                        if len(payment_arr)>= batch_size:
                            Payment.objects.bulk_create(payment_arr)
                            total_imported += len(payment_arr)
                            self.logger.info(f"Imported {len(payment_arr)} payments. Total: {total_imported}")
                            payment_arr = []
                    
                    if payment_arr:
                        Payment.objects.bulk_create(payment_arr)
                        total_imported += len(payment_arr)
                        self.logger.info(f"Imported final batch of {len(payment_arr)} payments. Total: {total_imported}")
                    
                self.reset_id("payments")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} payments in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during payments import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise

    def _get_status(self,row:str):
        if row == 'pending':
            return 'UNPAID'
        
        return row.upper()
    
    def _get_enrolment_type(self,row:str):
        ENROLMENT_TYPE = {
            'Enrolment':'ENROLMENT',
            'Advance':'ADVANCE',
            'Early_advance':'EARLY_ADVANCE',
            'Extend':'EXTEND',
            '3 Months Continuation':'EXTEND',
        }

        return ENROLMENT_TYPE[row]
    