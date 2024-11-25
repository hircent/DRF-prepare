from api.baseCommand import CustomBaseCommand
from category.models import Theme,Category
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import Theme'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_theme",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("theme.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    themes_arr = []
                    total_imported = 0
                    
                    order = 1
                    for row in reader:

                        try:
                            category = Category.objects.get(id=row['category_id'])
                        except Category.DoesNotExist:
                            self.logger.warning(f"Category with id {row['category_id']} does not exist.")

                        cat = Theme(
                            id = row['id'],
                            name = row['name'],
                            display_name = row['display_name'],
                            category = category,
                            order = order,
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        ) 
                        
                        themes_arr.append(cat)
                        self.stdout.write(self.style.SUCCESS(f"theme with id:{row['id']} has appended with {order} at time {datetime.now()}"))

                        if order >= 12:
                            order = 1
                        else:
                            order += 1
                        
                        if len(themes_arr)>= batch_size:
                            Theme.objects.bulk_create(themes_arr)
                            total_imported += len(themes_arr)
                            self.logger.info(f"Imported {len(themes_arr)} themes. Total: {total_imported}")
                            themes_arr = []
                            
                    if themes_arr:
                        Theme.objects.bulk_create(themes_arr)
                        total_imported += len(themes_arr)
                        self.logger.info(f"Imported final batch of {len(themes_arr)} themes. Total: {total_imported}")
                
                self.reset_id("themes")
                end_time = datetime.now()
                time_taken = start_time - end_time
                self.logger.info(f"Sucessfully imported {total_imported} themes in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = start_time - end_time
            self.logger.error(f"Error during theme import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise