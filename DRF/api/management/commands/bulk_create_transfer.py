from api.baseCommand import CustomBaseCommand
from django.db import transaction,connection
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from branches.models import Branch
from students.models import Students,StudentTransfer


class Command(CustomBaseCommand):
    help = 'Import Transfer In Out'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_transfer",__name__)
    
    def handle(self, *args, **options):
        file_path = self.get_csv_path("transfer.csv")
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting transfer in out import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    transfer_in_out_arr = []
                    total_imported = 0

                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} transfer_in_out in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during transfer import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
