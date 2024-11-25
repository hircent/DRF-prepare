from api.baseCommand import CustomBaseCommand
from django.db import transaction,connection
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from classes.models import Class ,StudentEnrolment
from branches.models import Branch
from category.models import Category, Grade
from students.models import Students

class Command(CustomBaseCommand):
    help = 'Import enrolments'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_enrolments",__name__)
    
    def handle(self, *args, **options):
        file_path = self.get_csv_path("enrolments.csv")
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting enrolments import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    enrolments = []
                    total_imported = 0

                    for row in reader:
                        
                        try:
                            branch = Branch.objects.get(id=row['branch'])
                        except Branch.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"Branch with id {row['branch']} does not exist. Skipping this row.")
                            continue

                        try:
                            student = Students.objects.get(id=row['student'])
                        except Students.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"Student with id {row['student']} does not exist. Skipping this row.")
                            continue
                        
                        try:
                            class_instance = Class.objects.get(id=row['class'])
                        except Class.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"Class with id {row['class']} does not exist. Skipping this row.")
                            continue
                        
                        try:
                            grade = Grade.objects.get(id=row['grade'])
                        except Grade.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"Grade with id {row['grade']} does not exist. Skipping this row.")
                            continue
                        
                        enrolment = StudentEnrolment(
                            id = row['id'],
                            student = student,
                            class_instance = class_instance,
                            branch = branch,
                            grade = grade,
                            enrollment_date = self.parse_date(row['start_date']),
                            is_active = self.parse_bool(row['is_active']),
                            remaining_lessons = row['remaining_lessons'],
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at']),
                        )

                        enrolments.append(enrolment)
                        self.stdout.write(self.style.SUCCESS(f"Enrolment with student id:{row['student']} has appended at time {datetime.now()}"))

                        if len(enrolments)>= batch_size:
                            StudentEnrolment.objects.bulk_create(enrolments)
                            total_imported += len(enrolments)
                            self.logger.info(f"Imported {len(enrolments)} enrolments. Total: {total_imported}")
                            enrolments = []
                            
                    if enrolments:
                        StudentEnrolment.objects.bulk_create(enrolments)
                        total_imported += len(enrolments)
                        self.logger.info(f"Imported final batch of {len(enrolments)} enrolments. Total: {total_imported}")
                
                self.reset_id("student_enrolments")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} enrolments in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during enrolment import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise