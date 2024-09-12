from django.core.management.base import BaseCommand
import csv
from accounts.models import User
from branches.models import Branch
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'import users from csv'

    def handle(self, *args, **kwargs):

        file_path = 'D:/python/deemcee/DRF-prepare/DRF/csv/users_role.csv'

        try:
            with open(file_path,'r') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    email_verified_at = timezone.make_aware(
                        datetime.strptime(row['email_verified_at'], "%Y-%m-%d %H:%M:%S")
                    )
                    created_at = timezone.make_aware(
                        datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S")
                    )
                    updated_at = timezone.make_aware(
                        datetime.strptime(row['updated_at'], "%Y-%m-%d %H:%M:%S")
                    )
                    # Check if the user exists by their email or username
                    user, created = User.objects.get_or_create(
                        username=row['username'],
                        defaults={
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'email': row['email'],
                            'email_verified_at': email_verified_at,
                            'branch': Branch.objects.get(id=row['branch_id']),
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
                        user.set_password('admin')  # Replace 'admin' with the password from CSV if available
                        user.save()

                    # Append roles to the existing user
                    user.roles.add(row['roles'])  # Assuming `roles` is a ForeignKey or ManyToManyField

                self.stdout.write(self.style.SUCCESS("Import users successful"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import users unsuccessful: {e}"))