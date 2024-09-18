from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path

class Command(BaseCommand):
    help = 'clean user profile'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    SAVE_TO = BASE_DIR / 'csv/user_profile_generated.csv'

    def handle(self, *args, **options) -> str | None:
        
        try:
            df = pd.read_csv(self.BASE_DIR/'csv/user_profile.csv')

            df['gender'] = df['gender'].str.lower()

            df.to_csv(self.SAVE_TO,index=False)
        
            self.stdout.write(self.style.SUCCESS("Clean user profile successful!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Clean user profile failed : {e}"))