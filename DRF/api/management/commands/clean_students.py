from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path

class Command(BaseCommand):
    help = 'clean students'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    SAVE_TO = BASE_DIR / 'csv/students_generated.csv'

    def handle(self, *args, **options) -> str | None:
        
        try:
            df = pd.read_csv(self.BASE_DIR/'csv/students.csv')

            # df['status'] = df['status'].str.lower()

            df.to_csv(self.SAVE_TO,index=False)
        
            self.stdout.write(self.style.SUCCESS("Clean students successful!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Clean students failed : {e}"))