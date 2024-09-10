from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Import data from an SQL file'

    def handle(self, *args, **kwargs):
        # Replace with the path to your SQL file
        file_path = 'D:/python/deemcee/DRF-prepare/DRF/branches.sql'
        # file_path = 'D:/python/DRF/DRF/branches.sql'

        try:
            with open(file_path, 'r', encoding='utf-8') as sqlfile:
                sql_content = sqlfile.read()

            with connection.cursor() as cursor:
                # Split SQL content into individual statements (assuming semicolon as delimiter)
                statements = sql_content.split(';')
                for statement in statements:
                    if statement.strip():  # Avoid empty statements
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error executing statement: {e}'))
                            
            self.stdout.write(self.style.SUCCESS('Successfully imported data from SQL file'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {e}'))

        '''
        Run this command if using Postgress
        '''
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('branches', 'id'), (SELECT MAX(id) FROM branches))")
                self.stdout.write(self.style.SUCCESS("Pg_get_serial_sequence for branch success"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Pg_get_serial_sequence error"))

        
