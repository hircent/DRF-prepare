from api.baseCommand import CustomBaseCommand
from payments.models import InvoiceSequence
from branches.models import Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import invoice sequence'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_invoice_sequence",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("invoice_sequence.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    invoice_sequence_arr = []
                    total_imported = 0

                    for row in reader:

                        try:
                            Branch.objects.get(id=row['branch_id'])
                        except (Branch.DoesNotExist) as e:
                            if isinstance(e, Branch.DoesNotExist):
                                self.logger.error(f"Branch with id {row['branch_id']} does not exist in the database.")
                                raise ImportError(f"Error while importing invoice sequences: {str(e)} {row}")
                            
                        (year,number) = self._get_year_and_number(row['number'])

                        invoice_sequence = InvoiceSequence(
                            id = row['id'],
                            branch_id = row['branch_id'],
                            number = number,
                            year = year
                        )

                        invoice_sequence_arr.append(invoice_sequence)

                        self.stdout.write(self.style.SUCCESS(f"Invoice sequences with id:{row['id']} at branch: {row['branch_id']} has appended at time {datetime.now()}"))

                        if len(invoice_sequence_arr)>= batch_size:
                            InvoiceSequence.objects.bulk_create(invoice_sequence_arr)
                            total_imported += len(invoice_sequence_arr)
                            self.logger.info(f"Imported {len(invoice_sequence_arr)} invoice sequences. Total: {total_imported}")
                            invoice_sequence_arr = []
                    
                    if invoice_sequence_arr:
                        InvoiceSequence.objects.bulk_create(invoice_sequence_arr)
                        total_imported += len(invoice_sequence_arr)
                        self.logger.info(f"Imported final batch of {len(invoice_sequence_arr)} invoice sequences. Total: {total_imported}")
                                         
                self.reset_id("invoice_sequences")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} invoice sequences in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during invoice sequences import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise

    def _get_year_and_number(self,row:str):
        year = '20'+row.split('-')[1]
        number = row.split('-')[2].replace('0','')

        return int(year),int(number)
    