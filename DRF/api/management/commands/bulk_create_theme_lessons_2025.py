from api.baseCommand import CustomBaseCommand
from category.models import Theme,ThemeLesson
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import Theme Lesson 2025'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_theme_lessons_2025",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("theme_lessons_2025.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    theme_lessons_arr = []
                    total_imported = 0

                    for row in reader:

                        try:
                            theme = Theme.objects.get(id=row['theme_id'])
                        except Theme.DoesNotExist:
                            self.logger.warning(f"Theme with id {row['theme_id']} does not exist.")

                        theme_lesson = ThemeLesson(
                            id = row['id'],
                            theme = Theme.objects.get(id=row['theme_id']),
                            name = row['display_name'],
                            order = row['order'],
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        ) 
                        
                        theme_lessons_arr.append(theme_lesson)
                        self.stdout.write(self.style.SUCCESS(f"theme with id:{row['id']} has appended at time {datetime.now()}"))
                        
                        if len(theme_lessons_arr)>= batch_size:
                            ThemeLesson.objects.bulk_create(theme_lessons_arr)
                            total_imported += len(theme_lessons_arr)
                            self.logger.info(f"Imported {len(theme_lessons_arr)} theme lessons. Total: {total_imported}")
                            theme_lessons_arr = []
                            
                    if theme_lessons_arr:
                        ThemeLesson.objects.bulk_create(theme_lessons_arr)
                        total_imported += len(theme_lessons_arr)
                        self.logger.info(f"Imported final batch of {len(theme_lessons_arr)} theme lessons. Total: {total_imported}")
                
                self.reset_id("theme_lessons")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} theme lessons in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during theme import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise