from typing import Any
from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path

class Command(BaseCommand):
    help = 'clean users and add infos，make sure total 15 columns after modified'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    SAVE_TO = BASE_DIR / 'csv/users_command_generated.csv'

    def handle(self, *args: Any, **options: Any) -> str | None:
        
        df = pd.read_csv(self.BASE_DIR/'csv/users_role12345.csv')

        df = self.add_column(['username','is_staff','is_active','is_superadmin','is_password_changed'],df)

        df = self.replace_value('is_active',1,df)
        df = self.replace_username(df)

        df.to_csv(self.SAVE_TO,index=False)

    def rearrange_column(self,column_order,df):
        df = df[column_order]
        return df

    def fill_in_username(self,column:str,df):

        df[column] = df['first_name'].replace(" ",'')

        return df
    
    def add_column(self,arr,df):

        for a in arr:
            if a == 'username':
                df[a] = None
            else :
                df[a] = 0

        
        return df
    
    def replace_value(self,column:str,value,df):

        df[column] = value

        return df

    def replace_username(self,df):
        df['username'] = df['first_name'].str.replace(" ",'').str.lower()

        return df
