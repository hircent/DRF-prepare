from django.contrib import admin
from .models import Calendar
# Register your models here.

class CalendarAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'entry_type', 'branch')
    list_filter = ('entry_type', 'branch')
    search_fields = ('title', 'description')
    ordering = ('start_date',)
    list_per_page = 10  

admin.site.register(Calendar, CalendarAdmin)
