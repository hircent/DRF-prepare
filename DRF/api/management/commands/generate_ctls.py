from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from datetime import datetime, timedelta
from pathlib import Path

from calendars.models import Calendar , CalendarThemeLesson
from category.models import Category
from branches.models import Branch
from django.db import transaction
from django.core.management.base import CommandError

class Command(BaseCommand):
    help = 'Generate Calendar Theme Lessons for branch'

    def add_arguments(self, parser: CommandParser) -> None:
        #python manage.py generate_ctls --branchId=1 --year=2024
        # parser.add_argument('--branchId', type=int, help='Branch ID')
        parser.add_argument('--year', type=int, help='Year')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # branch_id = kwargs['branchId']
        year = kwargs['year']

        # if not branch_id or not year:
        #     raise CommandError("Branch ID and Year are required")
        
        all_themes = self.get_cat_themes(year)
        
        branches_id = list(Branch.objects.all().values_list('id',flat=True))

        for id in branches_id:
            for theme in all_themes:
                self.generate_theme_lessons(theme,year,id)

                print(f"Theme lessons generated for branch {id} and year {year}")

    def generate_theme_lessons(self, themes, year, branch_id):
        """
        Generate theme lessons for a specific year and branch
        Ensures lessons start on January 1st but positioned correctly as if
        the sequence started on the previous Monday.
        """
        branch = Branch.objects.get(id=branch_id)
        blocked_dates = self.get_blocked_dates(year, branch_id)
        
        calendar_theme_lessons = []
        total_created = 0
        
        # Find what day of the week January 1st falls on
        jan_first = datetime(year, 1, 1).date()
        day_of_week = jan_first.weekday()  # 0 is Monday, 1 is Tuesday, etc.
        
        # Calculate what lesson day January 1st would be if the sequence started on a Monday
        # For example, if Jan 1 is Wednesday (day_of_week=2), it would be lesson day 3
        jan_first_lesson_day = day_of_week + 1  # +1 because we start counting from 1
        
        lesson_date = jan_first
        end_date = datetime(year, 12, 31).date()
        processed_themes_count = 0

        while lesson_date <= end_date and processed_themes_count < 12:
            for theme in themes:
                if processed_themes_count >= 12:
                    break
                for lesson in theme.theme_lessons.all():
                    # Start from the correct position in the sequence for January 1st
                    current_lesson_day = jan_first_lesson_day
                    current_lesson_date = lesson_date
                    lesson_days_created = 0

                    # For the first sequence starting on Jan 1, we need to create 
                    # (8 - jan_first_lesson_day) lessons to complete the 7-day cycle
                    lessons_to_create = 8 - jan_first_lesson_day if current_lesson_date == jan_first else 7

                    while lesson_days_created < lessons_to_create and current_lesson_date <= end_date:
                        # Skip blocked dates
                        if current_lesson_date not in blocked_dates:
                            ctl = CalendarThemeLesson(
                                theme_lesson=lesson,
                                theme=theme,
                                branch=branch,
                                lesson_date=current_lesson_date.strftime("%Y-%m-%d"),
                                day=current_lesson_date.strftime("%A"),
                                month=current_lesson_date.month,
                                year=current_lesson_date.year
                            )

                            calendar_theme_lessons.append(ctl)
                            lesson_days_created += 1
                            
                            # Increment the lesson day counter (1-7)
                            current_lesson_day = (current_lesson_day % 7) + 1

                            # Batch create to prevent memory issues
                            if len(calendar_theme_lessons) >= 500:
                                CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
                                total_created += 500
                                calendar_theme_lessons = []

                        # Move to next date regardless of whether a lesson was created
                        current_lesson_date += timedelta(days=1)

                    # After completing this lesson sequence, find the next Monday
                    next_monday = current_lesson_date
                    while next_monday.weekday() != 0:  # 0 is Monday
                        next_monday += timedelta(days=1)
                    lesson_date = next_monday

                    # Break out of loops if we've gone beyond the specified year
                    if lesson_date.year > year:
                        break

                # Break out of theme loop if we've gone beyond the specified year
                if lesson_date.year > year:
                    break

                processed_themes_count += 1

            # Break out of main loop if we've gone beyond the specified year
            if lesson_date.year > year:
                break

        # Create any remaining lessons
        if calendar_theme_lessons:
            CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
            total_created += len(calendar_theme_lessons)

        return total_created


    def get_blocked_dates(self,year,branch_id):
        all_events = Calendar.objects.filter(branch_id=branch_id,year=year,entry_type='centre holiday')

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
        cat = Category.objects.filter(year=year)

        if cat.count() != 3:
            raise CommandError(f"Expected 3 categories for year {year}, found {cat.count()}. Kindly contact admin!")

        kiddo_themes = cat[0].themes.all()
        kids_themes = cat[1].themes.all()
        superkids_themes = cat[2].themes.all()

        return [kiddo_themes,kids_themes,superkids_themes]