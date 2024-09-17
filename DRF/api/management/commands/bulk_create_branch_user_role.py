from typing import Any
from django.core.management import BaseCommand
from branches.models import UserBranchRole ,Branch
from accounts.models import User,Role
from pathlib import Path
from django.db import connection,transaction
from datetime import datetime
from csv import DictReader
import logging


class Command(BaseCommand):
    help = 'Import branch users role from csv'
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
        file_handler = logging.FileHandler(log_dir / 'branch_user_roles.log')
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
        file_path = self.BASE_DIR/'csv/users_role.csv'
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting branch user roles import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r') as file:
                    reader = DictReader(file)
                    branch_user_roles = []
                    total_imported = 0

                    for row in reader:
                        ubr = UserBranchRole(
                            user = User.objects.get(id=row['user_id']),
                            branch = Branch.objects.get(id=row['branch_id']),
                            role = Role.objects.get(id=row['role_id'])
                        )

                        branch_user_roles.append(ubr)
                        self.stdout.write(self.style.SUCCESS(f"User id:{row['user_id']} with branch_id {row['branch_id']} and role {row['role_id']} has appended at time {datetime.now()}"))

                        if(len(branch_user_roles) >= batch_size):
                            UserBranchRole.objects.bulk_create(branch_user_roles)
                            total_imported += len(branch_user_roles)
                            self.logger.info(f"Imported {len(branch_user_roles)} branch user roles. Total: {total_imported}")
                            branch_user_roles = []
                    
                    if branch_user_roles:
                        UserBranchRole.objects.bulk_create(branch_user_roles)
                        total_imported += len(branch_user_roles)
                        self.logger.info(f"Imported final batch of {len(branch_user_roles)} branch user roles. Total: {total_imported}")

                self.reset_id()
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Successfully imported {total_imported} branch user roles in total")
                self.logger.info(f"Time taken: {time_taken}")

        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during branch user roles import: {str(e)}")
            self.logger.error(f"Time taken: {time_taken}")
            # The transaction will be rolled back automatically
            raise


    def reset_id(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('user_branch_roles', 'id'), (SELECT MAX(id) FROM user_branch_roles))")
                self.logger.info("Pg_get_serial_sequence for user_branch_roles success")
        except Exception as e:
            self.logger.error("Pg_get_serial_sequence error")