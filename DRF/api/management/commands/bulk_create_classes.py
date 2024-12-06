from api.baseCommand import CustomBaseCommand
from django.db import transaction,connection
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from classes.models import Class
from branches.models import Branch
from category.models import Category

class Command(CustomBaseCommand):
    help = 'Import classes'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_classes",__name__)
    
    def handle(self, *args, **options):
        file_path = self.get_csv_path("classes_generated.csv")
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting classes import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    classes = []
                    total_imported = 0

                    for row in reader:
                        
                        try:
                            branch = Branch.objects.get(id=row['branch'])
                        except Branch.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"Branch with id {row['branch']} does not exist. Skipping this row.")
    
                        cl = Class(
                            id          = row['id'],
                            branch      = branch,
                            name        = self.get_category(index=int(row['category'])),
                            label       = row['label'],
                            start_date  = self.parse_date(row['commencement_date']),
                            start_time  = self.parse_time(row['start_time']),
                            end_time    = self.parse_time(row['end_time']),
                            day         = row['day'],
                            created_at  = self.parse_datetime(row['created_at']),
                            updated_at  = self.parse_datetime(row['updated_at']),
                        ) 
                        
                        classes.append(cl)
                        self.stdout.write(self.style.SUCCESS(f"Class with id:{row['id']} has appended at time {datetime.now()}"))
                        
                        if len(classes)>= batch_size:
                            Class.objects.bulk_create(classes)
                            total_imported += len(classes)
                            self.logger.info(f"Imported {len(classes)} classes. Total: {total_imported}")
                            classes = []
                            
                    if classes:
                        Class.objects.bulk_create(classes)
                        total_imported += len(classes)
                        self.logger.info(f"Imported final batch of {len(classes)} classes. Total: {total_imported}")
                
                self.reset_id("classes")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} classes in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during class import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
        
    def get_category(self,index):
        cate = {
            1:"Kiddo",
            2:"Kids",
            3:"Superkids"
        }
        
        return cate[index]