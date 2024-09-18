from django.core.management import BaseCommand
from pathlib import Path
from django.db import connection,transaction
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from accounts.models import User,UserProfile
import logging

class Command(BaseCommand):
    help = 'Import User Profile'
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
        file_handler = logging.FileHandler(log_dir / 'import_user_profile.log')
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
        file_path = self.BASE_DIR/'csv/user_profile_generated.csv'
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting branch user roles import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    user_profiles = []
                    total_imported = 0

                    for row in reader:
                        
                        try:
                            # Try to get the user by the provided user_id
                            user = User.objects.get(id=row['user_id'])
                        except User.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"User with id {row['user_id']} does not exist. Skipping this row.")
                            continue
                        
                        dob = row['dob'] if row['dob'] and row['dob'] != '\\N' else None
                        user_profile = UserProfile(
                            user = user,
                            gender = row['gender'],
                            dob = dob,
                            ic_number = row['ic_number'],
                            occupation = row['occupation'],
                            spouse_name = row['spouse_name'], 
                            spouse_phone = row['spouse_phone'], 
                            spouse_occupation = row['spouse_occupation'], 
                            # no_of_children = row['no_of_children'],
                            personal_email = row['personal_email'], 
                            bank_name = row['bank_name'], 
                            bank_account_name = row['bank_account_name'], 
                            bank_account_number = row['bank_account_number'], 
                            
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at']),
                        )

                        user_profiles.append(user_profile)
                        self.stdout.write(self.style.SUCCESS(f"User profile with user id:{row['user_id']} has appended at time {datetime.now()}"))

                        if(len(user_profiles) >= batch_size):
                            UserProfile.objects.bulk_create(user_profiles)
                            total_imported += len(user_profiles)
                            self.logger.info(f"Imported {len(user_profiles)} user profile. Total: {total_imported}")
                            user_profiles = []
                    
                    if user_profiles:
                        UserProfile.objects.bulk_create(user_profiles)
                        total_imported += len(user_profiles)
                        self.logger.info(f"Imported final batch of {len(user_profiles)} user profile. Total: {total_imported}")

                self.reset_id()
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Successfully imported {total_imported} user profile in total")
                self.logger.info(f"Time taken: {time_taken}")

        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during user profile import: {str(e)}")
            self.logger.error(f"Time taken: {time_taken}")
            # The transaction will be rolled back automatically
            raise

    @staticmethod
    def parse_datetime(value):
        return make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))

    def reset_id(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('user_profile', 'id'), (SELECT MAX(id) FROM user_profile))")
                self.logger.info("Pg_get_serial_sequence for user_profile success")
        except Exception as e:
            self.logger.error("Pg_get_serial_sequence error")