from calendars.models import Calendar
from datetime import timedelta, datetime, date
from typing import Set
from django.db.models import QuerySet
from classes.models import StudentEnrolment,StudentAttendance

class BlockedDatesMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._blocked_dates_cache = {}

    def _get_cached_blocked_dates(self, year, branch_id):
        cache_key = f"{year}_{branch_id}"
        if cache_key not in self._blocked_dates_cache:
            self._blocked_dates_cache[cache_key] = set(self._get_blocked_dates([year,datetime.today().year], branch_id))
        return self._blocked_dates_cache[cache_key]

    def _get_blocked_dates(self, year_list, branch_id):
        all_events = Calendar.objects.filter(branch_id=branch_id, year__in=year_list, entry_type='centre holiday')
        blocked_dates = []
        for event in all_events:
            start_date = event.start_datetime.date()
            end_date = event.end_datetime.date()
            if start_date == end_date:
                blocked_dates.append(start_date)
            else:
                while start_date <= end_date:
                    blocked_dates.append(start_date)
                    start_date += timedelta(days=1)
        return blocked_dates
    
    def _calculate_video_due_date_weeks(self,video_number):
        match int(video_number):
            case 1:
                weeks_remaining = 12
            case 2:
                weeks_remaining = 22
            case 3:
                weeks_remaining = 34
            case 4:
                weeks_remaining = 46

        return weeks_remaining
    
    def _get_blocked_date(self, branch_id: int, year: int) -> Set[date]:
        events = Calendar.objects.filter(
            branch_id=branch_id,
            year=year,
            entry_type='centre holiday'
        ).values_list('start_datetime', 'end_datetime')
        
        blocked_dates = set()
        
        for start_datetime, end_datetime in events:
            start_date = start_datetime.date()
            end_date = end_datetime.date()
            
            # If single day event
            if start_date == end_date:
                blocked_dates.add(start_date)
            else:
                # Add all dates in range
                current_date = start_date
                while current_date <= end_date:
                    blocked_dates.add(current_date)
                    current_date += timedelta(days=1)
                    
        return blocked_dates
    
    def _has_event(self,date,branch_id):
        blockedDate = self._get_blocked_date(branch_id=branch_id,year=date.year)
        
        return date in blockedDate
    

class UtilsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format_decimal_points(self, value, precision=2) -> str:
        return f"{float(value):,.{precision}f}"
    
    def calculate_end_date(self, obj:StudentEnrolment,blocked_dates):

        extensions_acount = obj.extensions.count()
        attendances : QuerySet[StudentAttendance] = obj.attendances.all()
        freeze_count = attendances.filter(status='FREEZED').count()
        remaining_lesson = obj.remaining_lessons

        student_should_have_remaining_lessons = (
            24 + 
            (extensions_acount * 12) + 
            freeze_count
        ) - 1

        if remaining_lesson == 0:
            return attendances.last().date
        
        if obj.start_date != obj.calculate_date:

            if attendances.exists():
                final_date = attendances.last().date
            else:
                final_date = obj.calculate_date
            while remaining_lesson > 0:
                final_date += timedelta(weeks=1)
                if final_date not in blocked_dates:
                    remaining_lesson -= 1
            
            return final_date
        
        else:
            
            final_date = obj.start_date

            while student_should_have_remaining_lessons > 0:
                final_date += timedelta(weeks=1)
                if final_date not in blocked_dates:
                    student_should_have_remaining_lessons -= 1
            
            return final_date

