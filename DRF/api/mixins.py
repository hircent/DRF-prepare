from calendars.models import Calendar
from datetime import timedelta, datetime

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
        all_events = Calendar.objects.filter(branch_id=branch_id, year__in=year_list)
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