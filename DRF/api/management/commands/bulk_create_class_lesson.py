from api.baseCommand import CustomBaseCommand
from accounts.models import User
from django.db import transaction,connection
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from classes.models import Class,ClassLesson
from branches.models import Branch
from category.models import Category

class Command(CustomBaseCommand):
    help = 'Import class_lessons'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_class_lessons",__name__)
    
    def handle(self, *args, **options):
        file_path = self.get_csv_path("class_lesson.csv")
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting class_lessons import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    class_lessons = []
                    total_imported = 0

                    for row in reader:
                        
                        try:
                            branch = Branch.objects.get(id=row['branch_id'])
                            class_instance = Class.objects.get(id=row['class_id'])
                            teacher = User.objects.get(id=row['teacher_id']) if row['teacher_id'] != '\\N' else None
                            co_teacher = User.objects.get(id=row['co_teacher_id']) if row['co_teacher_id'] != '\\N' else None
                        except (Branch.DoesNotExist,Class.DoesNotExist,User.DoesNotExist) as e:
                            raise ImportError(f"Error while importing class_lessons: {str(e)} {row}")
    
                        cl = ClassLesson(
                            id                  = row['id'],
                            branch              = branch,
                            class_instance      = class_instance,
                            teacher             = teacher,
                            co_teacher          = co_teacher,
                            theme_lesson        = row['display_name'],
                            date                = self.parse_date(row['date']),
                            start_datetime      = self.parse_datetime(row['actual_start_datetime']) if row['actual_start_datetime'] != '\\N' else None,
                            end_datetime        = self.parse_datetime(row['actual_end_datetime']) if row['actual_end_datetime'] != '\\N' else None,
                            status              = row['status'],
                            created_at          = self.parse_datetime(row['created_at']),
                            updated_at          = self.parse_datetime(row['updated_at']),
                        )
                        
                        class_lessons.append(cl)
                        self.stdout.write(self.style.SUCCESS(f"Class lesson with id:{row['id']} has appended at time {datetime.now()}"))
                        
                        if len(class_lessons)>= batch_size:
                            ClassLesson.objects.bulk_create(class_lessons)
                            total_imported += len(class_lessons)
                            self.logger.info(f"Imported {len(class_lessons)} class_lessons. Total: {total_imported}")
                            class_lessons = []
                            
                    if class_lessons:
                        ClassLesson.objects.bulk_create(class_lessons)
                        total_imported += len(class_lessons)
                        self.logger.info(f"Imported final batch of {len(class_lessons)} class_lessons. Total: {total_imported}")
                
                self.reset_id("class_lessons")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} class_lessons in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during class lessons import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
        