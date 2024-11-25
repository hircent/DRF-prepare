from api.baseCommand import CustomBaseCommand
from calendars.models import Calendar
from branches.models import Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import Calendar'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_calendar",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("calendar_generated.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    calendars_arr = []
                    total_imported = 0
                    
                    for row in reader:
                        
                        try:
                            # Try to get the user by the provided user_id
                            branch = Branch.objects.get(id=row['branch_id'])
                        except Branch.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"Branch with id {row['branch_id']} does not exist. Skipping this row.")
                            continue
                        cl = Calendar(
                            title = row['title'],
                            description = row['descriptions'],
                            start_datetime=self.parse_datetime(row['start_datetime']),
                            end_datetime=self.parse_datetime(row['end_datetime']),
                            entry_type = row['entry_type'],
                            month = self.parse_datetime(row['start_datetime']).month,
                            year = self.parse_datetime(row['start_datetime']).year,
                            branch = branch,
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        ) 
                        
                        calendars_arr.append(cl)
                        self.stdout.write(self.style.SUCCESS(f"Calendar with branch id:{row['branch_id']} has appended at time {datetime.now()}"))
                        
                        if len(calendars_arr)>= batch_size:
                            Calendar.objects.bulk_create(calendars_arr)
                            total_imported += len(calendars_arr)
                            self.logger.info(f"Imported {len(calendars_arr)} calendars. Total: {total_imported}")
                            calendars_arr = []
                            
                    if calendars_arr:
                        Calendar.objects.bulk_create(calendars_arr)
                        total_imported += len(calendars_arr)
                        self.logger.info(f"Imported final batch of {len(calendars_arr)} calendars. Total: {total_imported}")
                
                self.reset_id("calendars")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} calendars in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during calendar import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise