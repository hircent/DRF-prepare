from api.baseCommand import CustomBaseCommand
from classes.models import StudentAttendance,StudentEnrolment,ClassLesson,EnrolmentExtension
from branches.models import Branch
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
                    extension_arr = []
                    total_imported = 0
                    
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
    