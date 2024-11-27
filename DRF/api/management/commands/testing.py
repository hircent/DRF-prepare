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
        self.delete()


        # all_themes = self.get_cat_themes(2024)
        # for theme in all_themes:
        #     self.generate_theme_lessons(theme,2024,1)

        

    def delete(self):
        CalendarThemeLesson.objects.all().delete()
        print("Calendar theme lessons deleted")

    def generate_theme_lessons(self, themes, year, branch_id):
        """
        Generate theme lessons for a specific year and branch
        Ensures lessons are generated only for the specified year
        and completes 7 consecutive non-blocked days for each lesson
        """
        branch = Branch.objects.get(id=branch_id)
        blocked_dates = self.get_blocked_dates(year, branch_id)
        
        calendar_theme_lessons = []
        total_created = 0
        lesson_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()

        while lesson_date <= end_date:
            for theme in themes:
                for lesson in theme.theme_lessons.all():
                    # Track consecutive non-blocked days for this lesson
                    lesson_days_created = 0
                    current_lesson_date = lesson_date

                    while lesson_days_created < 7 and current_lesson_date <= end_date:
                        # Skip blocked dates
                        if current_lesson_date not in blocked_dates:
                            ctl = CalendarThemeLesson(
                                theme_lesson=lesson,
                                theme=theme,
                                branch=branch,
                                lesson_date=current_lesson_date.strftime("%Y-%m-%d"),
                                day=current_lesson_date.strftime("%A"),
                                month=current_lesson_date.month,
                                year=current_lesson_date.year,
                            )

                            calendar_theme_lessons.append(ctl)
                            lesson_days_created += 1

                            # Batch create to prevent memory issues
                            if len(calendar_theme_lessons) >= 500:
                                CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
                                total_created += 500
                                calendar_theme_lessons = []

                        # Move to next date regardless of whether a lesson was created
                        current_lesson_date += timedelta(days=1)

                        # Break if we've gone beyond the specified year
                        if current_lesson_date.year > year:
                            break

                    # Move lesson_date forward
                    lesson_date = current_lesson_date

                    # Break out of loops if we've gone into next year
                    if lesson_date.year > year:
                        break

                # Break out of theme loop if we've gone into next year
                if lesson_date.year > year:
                    break

            # Break out of main loop if we've gone into next year
            if lesson_date.year > year:
                break

        # Create any remaining lessons
        if calendar_theme_lessons:
            CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
            total_created += len(calendar_theme_lessons)

        return total_created

    def get_blocked_dates(self,year,branch_id):
        all_events = Calendar.objects.filter(branch_id=branch_id,year=year)

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