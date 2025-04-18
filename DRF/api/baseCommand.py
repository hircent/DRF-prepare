from django.core.management import BaseCommand
from datetime import datetime
from django.utils.timezone import make_aware
from django.db import connection
from pathlib import Path

import logging


class CustomBaseCommand(BaseCommand):
    help = 'Base class for custom import commands'
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    def setup_logger(self,filename,action_name):
        logger = logging.getLogger(action_name)
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create a file handler
        file_handler = logging.FileHandler(log_dir / f'{filename}.log')
        file_handler.setLevel(logging.INFO)
        
        # Create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(file_handler)
        
        return logger

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=500, help='Batch size for bulk create')

    def handle(self, *args, **options):
        raise NotImplementedError("Subclasses must implement handle() method")

    def get_csv_path(self, filename):
        return self.BASE_DIR / 'csv' / filename
    
    @staticmethod
    def parse_bool(value):
        return value.lower() in ('true', '1', 'yes')
    
    @staticmethod
    def parse_datetime(value):
        return make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    
    @staticmethod
    def parse_date(value):
        return make_aware(datetime.strptime(value, "%Y-%m-%d"))
    
    @staticmethod
    def parse_time(value):
        return make_aware(datetime.strptime(value, "%H:%M:%S"))
    
    @staticmethod
    def parse_datetime_to_date(value):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").date()
    
    @staticmethod
    def parse_date_to_time(value):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").time()

    def reset_id(self, table):
        try:
            with connection.cursor() as cursor:
                # This handles empty tables by using COALESCE to default to 1
                # The third parameter 'false' means the next value will be MAX(id) + 1, not MAX(id)
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT COALESCE(MAX(id), 0) FROM {table}), true)")
                self.logger.info(f"Pg_get_serial_sequence for {table} success")
        except Exception as e:
            self.logger.error(f"Pg_get_serial_sequence error: {str(e)}")

