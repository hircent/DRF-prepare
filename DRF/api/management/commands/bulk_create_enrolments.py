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
                            branch = Branch.objects.get(id=row['branch_id'])
                            student = Students.objects.get(id=row['student_id'])
                            classroom = Class.objects.get(id=row['class_id'])
                            grade = Grade.objects.get(id=row['grade_id'])
                        
                            enrolment = StudentEnrolment(
                                id = row['id'],
                                student = student,
                                classroom = classroom,
                                branch = branch,
                                grade = grade,
                                start_date = self.parse_date(row['start_date']),
                                is_active = self.parse_bool(row['is_active']),
                                created_at = self.parse_datetime(row['created_at']),
                                updated_at = self.parse_datetime(row['updated_at']),
                            )

                            enrolments.append(enrolment)
                            self.stdout.write(self.style.SUCCESS(f"Enrolment with id:{row['id']} has appended at time {datetime.now()}"))

                            if len(enrolments)>= batch_size:
                                StudentEnrolment.objects.bulk_create(enrolments)
                                total_imported += len(enrolments)
                                self.logger.info(f"Imported {len(enrolments)} enrolments. Total: {total_imported}")
                                enrolments = []
                        except (Branch.DoesNotExist, Students.DoesNotExist, Class.DoesNotExist, Grade.DoesNotExist) as e:
                            # Log the specific error and re-raise the exception
                            if isinstance(e, Branch.DoesNotExist):
                                self.logger.error(f"Branch with id {row['branch_id']} does not exist in the database.")
                                raise ValueError(f"Branch with id {row['branch_id']} does not exist.")
                            elif isinstance(e, Students.DoesNotExist):
                                self.logger.error(f"Student with id {row['student_id']} does not exist in the database.")
                                raise ValueError(f"Student with id {row['student_id']} does not exist.")
                            elif isinstance(e, Class.DoesNotExist):
                                self.logger.error(f"Class with id {row['class_id']} does not exist in the database.")
                                continue
                            elif isinstance(e, Grade.DoesNotExist):
                                self.logger.error(f"Grade with id {row['grade_id']} does not exist in the database.")
                                raise ValueError(f"Grade with id {row['grade_id']} does not exist.")
                            
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