import logging
from csv import DictReader
from django.core.management.base import BaseCommand
from accounts.models import User
from django.utils.timezone import make_aware
from datetime import datetime
from pathlib import Path
from django.db import connection,transaction
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Import users from CSV using bulk_create with logging'
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
        file_handler = logging.FileHandler(log_dir / 'user_import.log')
        file_handler.setLevel(logging.INFO)
        
        # Create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(file_handler)
        
        return logger

    def add_arguments(self, parser):
        # python manage.py import_users --batch-size 1000
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for bulk create')

    def handle(self, *args, **options):
        file_path = self.BASE_DIR/'csv/users_command_generated.csv'
        batch_size = options['batch_size']

        start_time = datetime.now()
        self.logger.info(f"Starting user import from {file_path}")
        default_hashed_password = make_password('password')

        try:
            with transaction.atomic():
                with open(file_path, 'r') as file:
                    reader = DictReader(file)
                    users = []
                    total_imported = 0

                    for row in reader:
                        user = User(
                            id=row['id'],
                            first_name=row['first_name'],
                            password=default_hashed_password,
                            email=row['email'],
                            username=row['username'],
                            last_name=row['last_name'],
                            created_at=self.parse_datetime(row['created_at']),
                            updated_at=self.parse_datetime(row['updated_at']),
                            last_login=self.parse_datetime(row['updated_at']),
                            is_active=self.parse_bool(row['is_active']),
                            is_staff=self.parse_bool(row['is_staff']),
                            is_superadmin=self.parse_bool(row['is_superadmin']),
                            is_password_changed=self.parse_bool(row['is_password_changed']),
                        )

                        # user.set_password('password')
                        users.append(user)
                        self.stdout.write(self.style.SUCCESS(f"User id:{row['id']} has appended at time {datetime.now()}"))

                        if len(users) >= batch_size:
                            User.objects.bulk_create(users)
                            total_imported += len(users)
                            self.logger.info(f"Imported {len(users)} users. Total: {total_imported}")
                            users = []

                    if users:
                        User.objects.bulk_create(users)
                        total_imported += len(users)
                        self.logger.info(f"Imported final batch of {len(users)} users. Total: {total_imported}")

                self.reset_id()
                
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Successfully imported {total_imported} users in total")
                self.logger.info(f"Time taken: {time_taken}")

        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during user import: {str(e)}")
            self.logger.error(f"Time taken: {time_taken}")
            # The transaction will be rolled back automatically
            raise

    def reset_id(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users))")
                self.logger.info("Pg_get_serial_sequence for users success")
        except Exception as e:
            self.logger.error("Pg_get_serial_sequence error")

    @staticmethod
    def parse_bool(value):
        return value.lower() in ('true', '1', 'yes')

    @staticmethod
    def parse_datetime(value):
        return make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))