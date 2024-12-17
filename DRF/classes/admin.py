from django.contrib import admin
from .models import Class,StudentEnrolment,ClassLesson,StudentAttendance

class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'label', 'start_time', 'end_time', 'day', 'branch')
    search_fields = ('name', 'label', 'description')
    list_filter = ('branch',)
    
class StudentEnrolmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student',  'branch', 'start_date', 'status', 'remaining_lessons')
    search_fields = ('student__name', )
    list_filter = ('status','branch','student__fullname',)

class ClassLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch','theme_lesson','theme_lesson__theme__name','teacher__username','status', 'date')
    search_fields = ('branch', 'theme_lesson','theme_lesson__theme__name')
    list_filter = ('status','branch',)

class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment__id','enrollment', 'branch', 'class_lesson','class_lesson__id', 'date', 'start_time', 'has_attended', 'status')
    search_fields = ('enrollment__student__fullname', 'class_lesson__theme_lesson__theme__name')
    list_filter = ('status','branch','enrollment__student__fullname','class_lesson__theme_lesson__theme__name')

admin.site.register(Class, ClassAdmin)    
admin.site.register(StudentEnrolment, StudentEnrolmentAdmin)
admin.site.register(ClassLesson, ClassLessonAdmin)
admin.site.register(StudentAttendance, StudentAttendanceAdmin)
# Register your models here.
