from django.contrib import admin
from .models import Class,StudentEnrolment,ClassLesson

class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'label', 'start_time', 'end_time', 'day', 'branch')
    search_fields = ('name', 'label', 'description')
    list_filter = ('branch',)
    
class StudentEnrolmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student',  'branch', 'start_date', 'status', 'remaining_lessons')
    search_fields = ('student__name', )
    list_filter = ('status','branch','student__fullname',)

class ClassLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_instance__name','theme_lesson','status', 'date')
    search_fields = ('class_instance__name', 'class_instance__label','status')
    list_filter = ('status','branch',)

admin.site.register(Class, ClassAdmin)    
admin.site.register(StudentEnrolment, StudentEnrolmentAdmin)
admin.site.register(ClassLesson, ClassLessonAdmin)
# Register your models here.
