from api.baseCommand import CustomBaseCommand
from django.db import transaction,connection
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from classes.models import Class
from branches.models import Branch
from category.models import Category, Grade
from students.models import Students

class Command(CustomBaseCommand):
    help = 'Import grades'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_grades",__name__)
    
    def handle(self, *args, **options):
        file_path = self.get_csv_path("grades.csv")
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting grades import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    grades = []
                    total_imported = 0

                    for row in reader:
                        
                        grade = Grade(
                            id = row['id'],
                            grade_level = row['id'],
                            category = row['category'],
                            price = row['price'],
                        )

                        grades.append(grade)
                        self.stdout.write(self.style.SUCCESS(f"grade with id:{row['id']} has appended at time {datetime.now()}"))

                        if len(grades)>= batch_size:
                            Grade.objects.bulk_create(grades)
                            total_imported += len(grades)
                            self.logger.info(f"Imported {len(grades)} grades. Total: {total_imported}")
                            grades = []
                            
                    if grades:
                        Grade.objects.bulk_create(grades)
                        total_imported += len(grades)
                        self.logger.info(f"Imported final batch of {len(grades)} grades. Total: {total_imported}")
                    
                
                self.reset_id("grades")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} grades in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during grade import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise