from django.core.management.base import BaseCommand
import pandas as pd
import numpy as np
from pathlib import Path

class Command(BaseCommand):
    help = 'clean students'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    SAVE_TO = BASE_DIR / 'csv/calendar_generated.csv'

    def handle(self, *args, **options) -> str | None:
        
        try:
            df = pd.read_csv(self.BASE_DIR/'csv/calendar.csv')

            df = df.replace("\\N",None)
            
            # Define conditions and choices for entry_type
            conditions = [
                df['title'].str.startswith("Centre Holiday"),
                df['title'].str.startswith("CMCO") | df['title'].str.startswith("MCO") | df['title'].str.startswith("System") |
                df['title'].str.startswith("Conditional") | df['title'].str.startswith("Movement Control")
            ]
            choices = ['centre holiday', 'other']

            # Create the new 'entry_type' column
            df['entry_type'] = np.select(conditions, choices, default='public holiday')

            df.to_csv(self.SAVE_TO,index=False)
        
            self.stdout.write(self.style.SUCCESS("Clean students successful!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Clean students failed : {e}"))