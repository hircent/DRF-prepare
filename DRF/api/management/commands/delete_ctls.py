from django.core.management.base import BaseCommand, CommandParser ,CommandError
from calendars.models import CalendarThemeLesson

class Command(BaseCommand):
    help = 'delete calendar theme lessons'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--branchId', type=int, help='Branch ID')
        parser.add_argument('--deleteAll', type=bool, help='Delete all Calendar Theme Lessons')
    def handle(self, *args, **kwargs):
        branch_id = kwargs['branchId']
        delete_all = kwargs['deleteAll']

        if delete_all:
            CalendarThemeLesson.objects.all().delete()
            print("All Calendar Theme Lessons deleted")
        else:
            if not branch_id:
                raise CommandError("Branch ID is required")
            ctls = CalendarThemeLesson.objects.filter(branch_id=branch_id)

            if not ctls.exists():
                raise CommandError(f"No Calendar Theme Lessons found for branch {branch_id}")
            
            ctls.delete()
            print(f"Calendar Theme Lessons for branch {branch_id} deleted")
        