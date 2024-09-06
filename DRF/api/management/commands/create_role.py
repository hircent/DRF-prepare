from django.core.management.base import BaseCommand
from accounts.models import Role  # Adjust the import based on your app's structure

class Command(BaseCommand):
    help = 'Create or delete initial roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete', 
            action='store_true', 
            help='Delete initial roles instead of creating them',
        )

    def handle(self, *args, **options):
        if options['delete']:
            self.delete_initial_roles()
        else:
            self.create_initial_roles()

    def create_initial_roles(self):
        roles = ['superadmin', 'admin', 'principal', 'manager', 'teacher','parent','student']
        for role_name in roles:
            if not Role.objects.filter(name=role_name).exists():
                Role.objects.create(name=role_name)
        self.stdout.write(self.style.SUCCESS('Successfully created initial roles'))

    def delete_initial_roles(self):
        roles_to_delete = ['superadmin', 'admin', 'principal', 'manager', 'teacher','parent','student']
        Role.objects.filter(name__in=roles_to_delete).delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted initial roles'))
