from api.baseCommand import CustomBaseCommand
from classes.models import StudentAttendance,StudentEnrolment,ClassLesson,EnrolmentExtension
from payments.models import Invoice, InvoiceSequence
from branches.models import Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import invoice'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_invoices",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("invoices.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()

        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    invoice_arr = []
                    total_imported = 0

                    for row in reader:

                        try:
                            Branch.objects.get(id=row['branch_id'])
                            InvoiceSequence.objects.get(id=row['invoice_sequence_id'])
                        except (Branch.DoesNotExist,InvoiceSequence.DoesNotExist) as e:
                            if isinstance(e, Branch.DoesNotExist):
                                self.logger.error(f"Branch with id {row['branch_id']} does not exist in the database.")
                                raise ImportError(f"Error while importing invoices: {str(e)} {row}")
                            if isinstance(e, InvoiceSequence.DoesNotExist):
                                self.logger.error(f"Invoice sequence with id {row['invoice_sequence_id']} does not exist in the database.")
                                raise ImportError(f"Error while importing invoices: {str(e)} {row}")
                            
                        invoice = Invoice(
                            id = row['id'],
                            branch_id = row['branch_id'],
                            invoice_sequence_id = row['invoice_sequence_id'],
                            file_path = row['file_path'],
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        )

                        invoice_arr.append(invoice)

                        self.stdout.write(self.style.SUCCESS(f"Invoices with id:{row['id']} at branch: {row['branch_id']} has appended at time {datetime.now()}"))

                        if len(invoice_arr)>= batch_size:
                            Invoice.objects.bulk_create(invoice_arr)
                            total_imported += len(invoice_arr)
                            self.logger.info(f"Imported {len(invoice_arr)} invoices. Total: {total_imported}")
                    
                    if invoice_arr:
                        Invoice.objects.bulk_create(invoice_arr)
                        total_imported += len(invoice_arr)
                        self.logger.info(f"Imported final batch of {len(invoice_arr)} invoices. Total: {total_imported}")
                    
                self.reset_id("invoices")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} invoices in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during invoices import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
    