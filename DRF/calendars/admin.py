from django.contrib import admin
from .models import Calendar, CalendarThemeLesson
# Register your models here.

class CalendarAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'start_datetime', 'end_datetime', 'entry_type', 'branch')
    list_filter = ('entry_type', 'branch')
    search_fields = ('title', 'description')
    ordering = ('start_datetime',)
    list_per_page = 10  

class CalendarThemeLessonAdmin(admin.ModelAdmin):
    list_display = ('theme_lesson', 'theme', 'theme__category__label', 'branch', 'lesson_date', 'day','year')
    list_filter = ('theme', 'branch','theme__category__label','day','year')
    search_fields = ('theme_lesson', 'theme', 'branch')
    ordering = ('lesson_date',)
    list_per_page = 50

admin.site.register(Calendar,CalendarAdmin)
admin.site.register(CalendarThemeLesson,CalendarThemeLessonAdmin)
