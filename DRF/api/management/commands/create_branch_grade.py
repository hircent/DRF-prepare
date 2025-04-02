from typing import Any
from django.core.management.base import BaseCommand
from django.db import connection
from branches.models import BranchGrade

class Command(BaseCommand):
    help = 'Initialise Branch Grade'

    def handle(self, *args: Any, **options: Any) -> None:

        data = [("Level 1", 20), ("Level 2", 15)]

        try:
            for level,percentage in data:
                BranchGrade.objects.create(name=level,percentage=percentage)
            
            self.stdout.write(self.style.SUCCESS("Branch grades created successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error : {e}"))