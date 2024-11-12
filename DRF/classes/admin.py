from django.contrib import admin
from .models import Class,StudentEnrolment

class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'label', 'start_time', 'end_time', 'day', 'branch')
    search_fields = ('name', 'label', 'description')
    list_filter = ('branch',)
    
class StudentEnrolmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'class_instance', 'branch', 'enrollment_date', 'is_active', 'remaining_lessons')
    search_fields = ('student__name', 'class_instance__name')
    list_filter = ('class_instance__branch',)

admin.site.register(Class, ClassAdmin)    
admin.site.register(StudentEnrolment, StudentEnrolmentAdmin)
# Register your models here.
