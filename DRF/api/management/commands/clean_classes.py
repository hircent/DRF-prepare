from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path

class Command(BaseCommand):
    help = 'clean classes'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    SAVE_TO = BASE_DIR / 'csv/classes_generated.csv'

    def handle(self, *args, **options) -> str | None:
        
        try:
            df = pd.read_csv(self.BASE_DIR/'csv/classes.csv')

            df = df.replace('\\N', None)

            df.to_csv(self.SAVE_TO,index=False)
        
            self.stdout.write(self.style.SUCCESS("Clean classes successful!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Clean classes failed : {e}"))