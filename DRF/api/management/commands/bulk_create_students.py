from django.core.management import BaseCommand
from pathlib import Path
from django.db import transaction,connection
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from students.models import Students
from accounts.models import User
from branches.models import Branch
import logging
import json
import ast

class Command(BaseCommand):
    help = 'Import students'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create a file handler
        file_handler = logging.FileHandler(log_dir / 'import_students.log')
        file_handler.setLevel(logging.INFO)
        
        # Create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(file_handler)
        
        return logger

    def add_arguments(self, parser):
        # python manage.py import_users --batch-size 1000
        parser.add_argument('--batch-size', type=int, default=500, help='Batch size for bulk create')

    def handle(self, *args, **options):
        file_path = self.BASE_DIR/'csv/students_generated.csv'
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting students import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    students = []
                    total_imported = 0

                    for row in reader:
                        try:
                            branch = Branch.objects.get(id=row['branch_id'])
                        except:
                            self.logger.error(f"Branch id {row['branch_id']} not found")
                            raise ValueError(f"Branch id {row['branch_id']} not found")
                        
                        student = Students(
                            id = row['id'],
                            branch = branch,
                            parent = User.objects.get(id=row['parent_id']),
                            first_name = row['first_name'],
                            fullname = row['first_name'],
                            gender = row['gender'],
                            dob = row['dob'],
                            school = 'SMK',
                            deemcee_starting_grade = row['deemcee_starting_grade'],
                            status = row['status'],
                            enrolment_date = row['enrolment_date'],
                            referral_channel = self.mapRefferalChannel(int(row['referral_channel_id'])),
                            referral = row['referral'] if row['referral'] != "N" else None,
                            starter_kits=self.parse_starter_kits(row['starter_kits']),
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at']),
                        )

                        students.append(student)
                        self.stdout.write(self.style.SUCCESS(f"Student id:{row['id']} has appended at time {datetime.now()}"))

                        if len(students) >= batch_size:
                            Students.objects.bulk_create(students)
                            total_imported += len(students)
                            self.logger.info(f"Imported {len(students)} students. Total: {total_imported}")
                            students = []

                    if students:
                        Students.objects.bulk_create(students)
                        total_imported += len(students)
                        self.logger.info(f"Imported final batch of {len(students)} students. Total: {total_imported}")
                
                self.reset_id()
                
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Successfully imported {total_imported} students in total")
                self.logger.info(f"Time taken: {time_taken}")


        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during student import: {str(e)}")
            self.logger.error(f"Time taken: {time_taken}")
            # The transaction will be rolled back automatically
            raise

    @staticmethod
    def parse_datetime(value):
        return make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    
    def reset_id(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('students', 'id'), (SELECT MAX(id) FROM students))")
                self.logger.info("Pg_get_serial_sequence for students success")
        except Exception as e:
            self.logger.error("Pg_get_serial_sequence error")

    def mapRefferalChannel(self,referral_channel):
        channel = {
            1:'Facebook',
            2:'Google Form',
            3:'Centre FB Page',
            4:'DeEmcee Referral',
            5:'External Referral',
            6:'Call In',
            7:'Others'
        }

        return channel.get(referral_channel)
    
    
    def parse_starter_kits(self,json_string):
        """
        Parse a JSON string into a Python list, with error handling
        """
        if not json_string or json_string == '[]':
            return []
            
        try:
            # Method 1: Try direct JSON parsing
            return json.loads(json_string)
        except json.JSONDecodeError:
            try:
                # Method 2: Try cleaning the string and parsing
                # Remove single quotes and replace with double quotes
                cleaned_string = json_string.replace("'", '"')
                return json.loads(cleaned_string)
            except json.JSONDecodeError:
                try:
                    # Method 3: Try using ast.literal_eval
                    return ast.literal_eval(json_string)
                except (ValueError, SyntaxError):
                    # If all parsing methods fail, return empty list
                    return []