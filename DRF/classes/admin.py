from django.contrib import admin
from .models import (
    Class,StudentEnrolment,ClassLesson,StudentAttendance,
    EnrolmentExtension,VideoAssignment
)

class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'label', 'start_time', 'end_time', 'day', 'branch')
    search_fields = ('name', 'label', 'description')
    list_filter = ('branch',)
    
class StudentEnrolmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student',  'branch', 'start_date', 'status', 'remaining_lessons','is_active',)
    search_fields = ('student__name', )
    list_filter = ('status','branch','student__fullname','is_active',)

class ClassLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch','theme_lesson','theme_lesson__theme__name','teacher__username','status', 'date')
    search_fields = ('branch', 'theme_lesson','theme_lesson__theme__name')
    list_filter = ('status','branch',)

class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment__id','enrollment', 'branch', 'class_lesson','class_lesson__id', 'date', 'start_time', 'has_attended', 'status')
    search_fields = ('enrollment__student__fullname', 'class_lesson__theme_lesson__theme__name')
    list_filter = ('status','branch','enrollment__student__fullname','enrollment__id',)

class EnrolmentExtensionAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrolment','enrolment__id', 'branch', 'start_date')
    search_fields = ('enrolment__student__fullname',)
    list_filter = ('branch','enrolment__student__fullname',)

class VideoAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrolment__student__fullname', 'theme', 'video_url', 'video_number', 'submission_date')
    search_fields = ('enrolment__student__fullname',)
    list_filter = ('enrolment__student__fullname','enrolment__branch')

admin.site.register(Class, ClassAdmin)    
admin.site.register(StudentEnrolment, StudentEnrolmentAdmin)
admin.site.register(ClassLesson, ClassLessonAdmin)
admin.site.register(StudentAttendance, StudentAttendanceAdmin)
admin.site.register(EnrolmentExtension, EnrolmentExtensionAdmin)
admin.site.register(VideoAssignment, VideoAssignmentAdmin)
# Register your models here.
