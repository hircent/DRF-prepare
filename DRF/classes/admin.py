from django.contrib import admin
from .models import Class,StudentEnrolment,ClassLesson

class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'label', 'start_time', 'end_time', 'day', 'branch')
    search_fields = ('name', 'label', 'description')
    list_filter = ('branch',)
    
class StudentEnrolmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student',  'branch', 'enrollment_date', 'is_active', 'remaining_lessons')
    search_fields = ('student__name', )

class ClassLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_instance', 'theme', 'lesson_number', 'lesson_content', 'lesson_date', 'theme_order', 'is_completed')
    search_fields = ('class_instance__name', 'class_instance__label', 'theme__name', 'lesson_content')

admin.site.register(Class, ClassAdmin)    
admin.site.register(StudentEnrolment, StudentEnrolmentAdmin)
admin.site.register(ClassLesson, ClassLessonAdmin)
# Register your models here.
