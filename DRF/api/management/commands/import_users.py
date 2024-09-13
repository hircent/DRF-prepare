from django.core.management.base import BaseCommand
import csv
from accounts.models import User
from django.utils import timezone
from datetime import datetime
from pathlib import Path
from django.db import connection,transaction


class Command(BaseCommand):
    help = 'import users from csv'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

    def handle(self, *args, **kwargs):

        file_path = self.BASE_DIR/'csv/users_command_generated.csv'
        start_time = datetime.now()

        try:
            with transaction.atomic():
                with open(file_path,'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        created_at = timezone.make_aware(
                            datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S")
                        )
                        updated_at = timezone.make_aware(
                            datetime.strptime(row['updated_at'], "%Y-%m-%d %H:%M:%S")
                        )
                        # Check if the user exists by their email or username
                        user, created = User.objects.update_or_create(
                            id=row['id'],
                            defaults={
                                'username': row['username'],
                                'first_name': row['first_name'],
                                'email': row['email'],
                                'created_at': created_at,
                                'updated_at': updated_at,
                                'last_login': updated_at,
                                'is_active': row['is_active'],
                                'is_staff': row['is_staff'],
                                'is_superadmin': row['is_superadmin'],
                                'is_password_changed': row['is_password_changed'],
                            }
                        )

                        # If the user was just created, set the password
                        if created:
                            user.set_password('password')  # Replace 'admin' with the password from CSV if available
                            user.save()
                            print(f"User id {row['id']} created")
                    
            self.reset_id()

            ended_time = datetime.now()
            time_taken = ended_time - start_time
            self.stdout.write(self.style.SUCCESS("Import users successful"))
            self.stdout.write(self.style.SUCCESS(f" Started time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}"))
            self.stdout.write(self.style.SUCCESS(f" Ended time: {ended_time.strftime('%Y-%m-%d %H:%M:%S')}"))
            self.stdout.write(self.style.SUCCESS(f"Time taken: {time_taken}"))
        except Exception as e:
            ended_time = datetime.now()
            time_taken = ended_time - start_time
            self.stdout.write(self.style.ERROR(f"Import users unsuccessful: {e} {row}"))
            self.stdout.write(self.style.ERROR(f" Started time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}"))
            self.stdout.write(self.style.ERROR(f" Ended time: {ended_time.strftime('%Y-%m-%d %H:%M:%S')}"))
            self.stdout.write(self.style.ERROR(f"Time taken: {time_taken}"))

    def reset_id(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users))")
                self.stdout.write(self.style.SUCCESS("Pg_get_serial_sequence for users success"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Pg_get_serial_sequence error"))