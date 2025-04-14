from django.contrib import admin
from .models import (
    Class,StudentEnrolment,ClassLesson,StudentAttendance,
    EnrolmentExtension,VideoAssignment,ReplacementAttendance
)

class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'label', 'start_time', 'end_time', 'day', 'branch')
    search_fields = ('name', 'label', 'description')
    list_filter = ('branch',)
    
class StudentEnrolmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student',  'branch', 'start_date', 'calculate_date', 'status', 'remaining_lessons','is_active',)
    search_fields = ('student__name', )
    list_filter = ('status','branch','student__fullname','is_active',)

class ClassLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch','theme_lesson','theme_lesson__theme__name','teacher__username','status', 'date')
    search_fields = ('branch', 'theme_lesson','theme_lesson__theme__name')
    list_filter = ('status','branch',)

    raw_id_fields = ('theme_lesson','teacher','branch')

class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment__id','enrollment', 'branch', 'class_lesson','class_lesson__id', 'date', 'start_time', 'has_attended', 'status')
    search_fields = ('enrollment__student__fullname', 'class_lesson__theme_lesson__theme__name')
    list_filter = ('status','branch','enrollment__student__fullname','enrollment__id',)

    raw_id_fields = ('enrollment', 'class_lesson','branch')

class EnrolmentExtensionAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrolment','enrolment__id', 'branch', 'start_date','status')
    search_fields = ('enrolment__student__fullname',)
    list_filter = ('branch','enrolment__student__fullname',)

    raw_id_fields = ('enrolment','branch')

class VideoAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrolment__student__fullname', 'theme', 'video_url', 'video_number', 'submission_date')
    search_fields = ('enrolment__student__fullname',)
    list_filter = ('enrolment__student__fullname','enrolment__branch')

    raw_id_fields = ('enrolment','theme')

class ReplacementAttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'attendances','attendances_id', 'class_instance', 'date', 'status')
    list_select_related = ('attendances', 'class_instance')  # Reduce database queries
    
    search_fields = ('attendances__enrollment__student__fullname',)
    list_filter = ('status', 'date')
    
    # Optimize the form for adding/editing
    raw_id_fields = ('attendances', 'class_instance')  # Replace dropdown with search input
    
    # If you need to show related fields in the form
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'attendances',
            'class_instance',
            'attendances__enrollment__student'
        )
    
admin.site.register(Class, ClassAdmin)    
admin.site.register(StudentEnrolment, StudentEnrolmentAdmin)
admin.site.register(ClassLesson, ClassLessonAdmin)
admin.site.register(StudentAttendance, StudentAttendanceAdmin)
admin.site.register(EnrolmentExtension, EnrolmentExtensionAdmin)
admin.site.register(VideoAssignment, VideoAssignmentAdmin)
admin.site.register(ReplacementAttendance, ReplacementAttendanceAdmin)
# Register your models here.
