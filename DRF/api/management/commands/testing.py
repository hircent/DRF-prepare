from django.core.management.base import BaseCommand

from branches.models import Branch
from calendars.models import CalendarThemeLesson
import datetime
class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        cate = {
            1:"Kids",
            2:"Kiddo",
            3:"Superkids"
        }
        
        print(cate[1])