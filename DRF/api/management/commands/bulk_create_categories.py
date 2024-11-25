from api.baseCommand import CustomBaseCommand
from category.models import Category
from branches.models import Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import Category'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_categories",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("categories.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    categoriess_arr = []
                    total_imported = 0
                    
                    for row in reader:
                        
                        cat = Category(
                            id = row['id'],
                            name = row['name'],
                            year = datetime.now().year,
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        ) 
                        
                        categoriess_arr.append(cat)
                        self.stdout.write(self.style.SUCCESS(f"categories with id:{row['id']} has appended at time {datetime.now()}"))
                        
                        if len(categoriess_arr)>= batch_size:
                            Category.objects.bulk_create(categoriess_arr)
                            total_imported += len(categoriess_arr)
                            self.logger.info(f"Imported {len(categoriess_arr)} categoriess. Total: {total_imported}")
                            categoriess_arr = []
                            
                    if categoriess_arr:
                        Category.objects.bulk_create(categoriess_arr)
                        total_imported += len(categoriess_arr)
                        self.logger.info(f"Imported final batch of {len(categoriess_arr)} categoriess. Total: {total_imported}")
                
                self.reset_id("categories")
                end_time = datetime.now()
                time_taken = start_time - end_time
                self.logger.info(f"Sucessfully imported {total_imported} categoriess in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = start_time - end_time
            self.logger.error(f"Error during categories import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise