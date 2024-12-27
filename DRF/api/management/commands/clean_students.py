from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path
import json
import ast

class Command(BaseCommand):
    help = 'clean students'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    SAVE_TO = BASE_DIR / 'csv/students_generated.csv'

    def handle(self, *args, **options) -> str | None:
        
        try:
            df = pd.read_csv(
                self.BASE_DIR/'csv/students.csv',
                quoting=1,
                escapechar='\\',
                doublequote=True,
                encoding='utf-8',
                na_values=['\\N', 'NULL', ''],  # Recognize \N as NULL
                keep_default_na=False  # Don't convert other strings to NA
            )

            # df = df.replace("N", '')

            if 'starter_kits' in df.columns:
                df['starter_kits'] = df['starter_kits'].apply(self.clean_json_field)

            df = df.fillna({
                'starter_kits': '[]',
                'referral': '',
                'school': 'SMK',
            })

            

            # Save with proper quoting to handle JSON fields
            df.to_csv(
                self.SAVE_TO, 
                index=False,
                quoting=1,  # QUOTE_ALL
                escapechar='\\',
                doublequote=True,
                encoding='utf-8'
            )
        
            self.stdout.write(self.style.SUCCESS("Clean students successful!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Clean students failed : {e}"))

    def clean_json_field(self, value):
        """Clean JSON field to ensure proper format"""
        try:
            if isinstance(value, str):
                try:
                    # Try parsing as JSON first
                    parsed = json.loads(value)
                    return json.dumps(parsed)
                except json.JSONDecodeError:
                    try:
                        # Try parsing as Python literal if JSON fails
                        parsed = ast.literal_eval(value)
                        return json.dumps(parsed)
                    except (ValueError, SyntaxError):
                        return '[]'
            elif isinstance(value, (list, dict)):
                return json.dumps(value)
            else:
                return '[]'
        except Exception:
            return '[]'