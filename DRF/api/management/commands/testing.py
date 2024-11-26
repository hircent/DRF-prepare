from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from pathlib import Path

from calendars.models import Calendar , CalendarThemeLesson
from category.models import Category
from branches.models import Branch

class Command(BaseCommand):
    help = 'testing function'

    def handle(self, *args, **kwargs):
        # self.delete()


        all_themes = self.get_cat_themes(2024)
        for theme in all_themes:
            self.generate_theme_lessons(theme,2024,2)

        

    def delete(self):
        CalendarThemeLesson.objects.all().delete()
        print("Calendar theme lessons deleted")

    def generate_theme_lessons(self,themes,year,branch_id):
        blockedDate = self.get_blocked_dates(year)
        cat_2024 = Category.objects.filter(year=year)
        branch = Branch.objects.get(id=branch_id)
        if cat_2024.exists() and cat_2024.count() == 3:
            print("Category exists")

        
        calendar_theme_lessons = []
        total_created = 0
        lesson_date_2024 = datetime(2024,1,1).date()

        while lesson_date_2024 <= datetime(2024,12,31).date():
            
            for theme in themes:

                for lesson in theme.theme_lessons.all():

                    #Each lesson has to 7 days consecutively
                    for i in range(0,7):
                        if lesson_date_2024 not in blockedDate:
                            ctl = CalendarThemeLesson(
                                theme_lesson=lesson,
                                theme=theme,
                                branch=branch,
                                lesson_date=lesson_date_2024.strftime("%Y-%m-%d"),
                                day=lesson_date_2024.strftime("%A"),
                                month=lesson_date_2024.month
                            )

                            calendar_theme_lessons.append(ctl)
                            lesson_date_2024 += timedelta(days=1)
                        else:
                            lesson_date_2024 += timedelta(days=1)

                        if len(calendar_theme_lessons) >= 500:
                            CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
                            total_created += 500
                            print(f"{total_created} Calendar theme lessons created")
                            calendar_theme_lessons = []

        if calendar_theme_lessons:
            CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
            total_created += len(calendar_theme_lessons)
            print(f"{total_created} Calendar theme lessons created")

    def get_blocked_dates(self,year):
        all_events = Calendar.objects.filter(branch_id=1,year=year)

        blockedDate = []

        for event in all_events:
            
            start_date = event.start_datetime.date()
            end_date = event.end_datetime.date()

            if start_date == end_date:
                blockedDate.append(start_date)
            else:

                while start_date <= end_date:
                    blockedDate.append(start_date)
                    start_date += timedelta(days=1)
        
        return blockedDate
    
    def get_cat_themes(self,year):
        kiddo_themes = Category.objects.filter(year=year)[0].themes.all()
        kids_themes = Category.objects.filter(year=year)[1].themes.all()
        superkids_themes = Category.objects.filter(year=year)[2].themes.all()

        return [kiddo_themes,kids_themes,superkids_themes]