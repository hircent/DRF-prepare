from api.mixins import BlockedDatesMixin
from branches.models import Branch

from category.models import Theme
from calendars.models import Calendar
from .models import (
    Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension, VideoAssignment,
    ReplacementAttendance
)
from category.serializers import ThemeLessonAndNameDetailsSerializer
from django.db.models import F,Value
from django.utils import timezone
from datetime import timedelta ,  datetime
from rest_framework import serializers


'''
Video Assignment Serializer
'''
class VideoAssignmentListSerializer(BlockedDatesMixin,serializers.ModelSerializer):
    submit_due_date = serializers.SerializerMethodField()

    class Meta:
        model = VideoAssignment
        fields = ['id','video_number','submission_date','submit_due_date']
    
    def get_submit_due_date(self, obj):
        blockedDate = self._get_cached_blocked_dates(obj.enrolment.start_date.year, obj.enrolment.branch.id)

        current_date = obj.enrolment.start_date

        weeks_remaining = self._calculate_video_due_date_weeks(obj.video_number)

        while weeks_remaining > 0:
            current_date += timedelta(weeks=1)
            if current_date not in blockedDate:
                weeks_remaining -= 1

        return current_date.strftime("%Y-%m-%d")
    
class VideoAssignmentDetailsSerializer(BlockedDatesMixin,serializers.ModelSerializer):
    submit_due_date = serializers.SerializerMethodField()

    class Meta:
        model = VideoAssignment
        fields = ['id','theme','video_url','video_number','submission_date','submit_due_date']

    def get_submit_due_date(self, obj):
        blockedDate = self._get_cached_blocked_dates(obj.enrolment.start_date.year, obj.enrolment.branch.id)

        current_date = obj.enrolment.start_date

        weeks_remaining = self._calculate_video_due_date_weeks(obj.video_number)

        while weeks_remaining > 0:
            current_date += timedelta(weeks=1)
            if current_date not in blockedDate:
                weeks_remaining -= 1

        return current_date.strftime("%Y-%m-%d")
    
class VideoAssignmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoAssignment
        fields = ['id','theme','video_url','submission_date']
    
    def validate_theme(self, value):
        if value and not Theme.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid Theme ID.")
        return value
        
    def validate_video_url(self, value):
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Invalid URL format.")
        return value

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        instance.save()
        return instance
       
'''
Student Enrolment Serializer
'''
class StudentEnrolmentListForParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = [
            'id','start_date','status','remaining_lessons','is_active','freeze_lessons','grade'
        ]

class StudentEnrolmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = '__all__'
        
class StudentEnrolmentListForClassSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    future_remaining_lessons = serializers.IntegerField(read_only=True)

    class Meta:
        model = StudentEnrolment
        fields = ['id', 'student','is_active','remaining_lessons','future_remaining_lessons']

    def get_student(self, obj):
        return { "id": obj.student.id, "fullname": obj.student.fullname }

class StudentEnrolmentDetailsSerializer(BlockedDatesMixin,serializers.ModelSerializer):
    end_date = serializers.SerializerMethodField()
    video_assignments = VideoAssignmentListSerializer(many=True)

    class Meta:
        model = StudentEnrolment
        fields = [
            'id','start_date','end_date','status',
            'remaining_lessons','is_active','freeze_lessons',
            'grade','video_assignments'
        ]

    def get_end_date(self, obj):
        blocked_dates = self._get_cached_blocked_dates(obj.start_date.year, obj.branch.id)
    
        today = datetime.today().date()
        target_weekday = obj.start_date.weekday()
        initial_weekday = today.weekday()
        
        # Calculate initial days to reach target weekday
        days_to_add = (target_weekday - initial_weekday) % 7
        
        # Start with today's date
        current_date = today + timedelta(days=days_to_add)
        weeks_remaining = obj.remaining_lessons
        
        # Count weeks, skipping blocked dates
        while weeks_remaining > 0:
            current_date += timedelta(weeks=1)
            if current_date not in blocked_dates:
                weeks_remaining -= 1
        
        return current_date.strftime("%Y-%m-%d")

'''
Student Attendance Serializer
'''
class StudentAttendanceListSerializer(serializers.ModelSerializer):
    enrollment = serializers.SerializerMethodField()

    class Meta:
        model = StudentAttendance
        fields = ['id','enrollment','status']

    def get_enrollment(self, obj):
        return { 
            "id": obj.enrollment.id, 
            "student": {
                "id": obj.enrollment.student.id,
                "fullname": obj.enrollment.student.fullname
            } 
        }

'''
Class Serializer
'''
class ClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id','branch','name','label','start_date','start_time','end_time','day']

class ClassDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id','name','label','start_time','end_time','day']



'''
Class Enrolment (Check For Future Lessons)
'''
class ClassEnrolmentListSerializer(serializers.ModelSerializer):
    unmarked_enrolments = serializers.SerializerMethodField()
    class_instance = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id','branch','class_instance','unmarked_enrolments']

    def get_unmarked_enrolments(self, obj):
        check_after_week = self.context.get('check_after_week')

        enrolments = obj.enrolments.annotate(
            future_remaining_lessons= F('remaining_lessons') - Value(check_after_week)
        ).filter(
            future_remaining_lessons__gt=0,
            is_active=True
        )

        serializer = StudentEnrolmentListForClassSerializer(enrolments, many=True)


        return serializer.data
    
    def get_class_instance(self, obj):
        return {
            "name": obj.name,
            "label": obj.label,
            "start_time": obj.start_time,
            "end_time": obj.end_time,
            "day": obj.day
        }

class ClassCreateUpdateSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        error_messages={
            'does_not_exist': 'Invalid Branch.',
        }
    )

    class Meta:
        model = Class
        fields = [
            'id',
            'branch',
            'name',
            'label',
            'start_date',
            'start_time',
            'end_time',
            'day',
        ]

    def create(self, validated_data):
        # Pop the branch and category data from the validated data
        branch_data = validated_data.pop("branch", None)
        
        branch_data = Branch.objects.get(id=branch_data.id)
        # Create the class instance
        class_instance = Class.objects.create(branch=branch_data, **validated_data)

        return class_instance
    
'''
Class Lesson Serializer (Check For Attended Lessons)
'''

class ClassLessonListSerializer(serializers.ModelSerializer):
    student_attendances = serializers.SerializerMethodField()
    class_instance = ClassDetailsSerializer(read_only=True)

    class Meta:
        model = ClassLesson
        fields = ['id','branch','class_instance','teacher','co_teacher','theme_lesson','date','status','student_attendances']

    def get_student_attendances(self, obj):
        attendances = obj.attendances.all().select_related(
            'enrollment__student',
            'enrollment__classroom'
        ).prefetch_related('replacement_attendances')
        
        serialized_attendances = []
        
        for attendance in attendances:
            attendance_data = StudentAttendanceListSerializer(attendance).data
            # If status is replacement, add replacement attendance info
            if attendance.status == 'REPLACEMENT':
                replacement = attendance.replacement_attendances.first()  # Get the latest replacement
                print(replacement)
                if replacement:
                    attendance_data['replacement_class_info'] = {
                        'id': replacement.class_instance.id,
                        'label': replacement.class_instance.label,
                        'date': replacement.date
                    }
            
            serialized_attendances.append(attendance_data)
            
        return serialized_attendances
    
class ClassLessonDetailsSerializer(serializers.ModelSerializer):
    theme_lesson = ThemeLessonAndNameDetailsSerializer(many=False)

    class Meta:
        model = ClassLesson
        fields = ['id','theme_lesson']
    
class TodayClassLessonSerializer(serializers.ModelSerializer):
    student_attendances = serializers.SerializerMethodField()
    class_instance = ClassDetailsSerializer(read_only=True)
    unmarked_enrolments = serializers.SerializerMethodField()

    class Meta:
        model = ClassLesson
        fields = ['id', 'branch', 'class_instance', 'teacher', 'co_teacher', 'theme_lesson', 'date', 'status', 'student_attendances', 'unmarked_enrolments']

    def get_student_attendances(self, obj):
        attendances = obj.attendances.all().select_related(
            'enrollment__student',
            'enrollment__classroom'
        ).prefetch_related('replacement_attendances')
        
        serialized_attendances = []
        
        for attendance in attendances:
            attendance_data = StudentAttendanceListSerializer(attendance).data
            # If status is replacement, add replacement attendance info
            if attendance.status == 'REPLACEMENT':
                replacement = attendance.replacement_attendances.first()  # Get the latest replacement
                print(replacement)
                if replacement:
                    attendance_data['replacement_class_info'] = {
                        'id': replacement.class_instance.id,
                        'label': replacement.class_instance.label,
                        'date': replacement.date
                    }
            
            serialized_attendances.append(attendance_data)
            
        return serialized_attendances
    
    def get_unmarked_enrolments(self, obj):
        # Get all active enrollments for this class
        all_enrollments = obj.class_instance.enrolments.filter(is_active=True)
        # Get IDs of students who already have attendance marked
        marked_student_ids = obj.attendances.values_list('enrollment__student__id', flat=True)
        # Filter enrollments to get only unmarked students
        unmarked_enrollments = all_enrollments.exclude(student__id__in=marked_student_ids)
        
        return StudentEnrolmentListForClassSerializer(unmarked_enrollments, many=True).data

'''
Time Slot Serializer
'''
class TimeslotListSerializer(serializers.ModelSerializer):
    student_in_class = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id','label','day','student_in_class']

    def get_student_in_class(self, obj):
        check_after_week = self.context.get('check_after_week')

        enrolments = obj.enrolments.annotate(
            future_remaining_lessons= F('remaining_lessons') - Value(check_after_week)
        ).filter(
            future_remaining_lessons__gt=0,
            is_active=True
        )

        return len(enrolments)

class EnrolmentLessonListSerializer(serializers.ModelSerializer):
    class_lesson = ClassLessonDetailsSerializer(read_only=True)

    class Meta:
        model = StudentAttendance
        fields = ['id','class_lesson','date','day','start_time','end_time','has_attended','status']

class EnrolmentExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = ['id','remaining_lessons']

    def update(self, instance, validated_data):

        enrolmentExt,created = EnrolmentExtension.objects.get_or_create(
            enrolment=instance, 
            branch=instance.branch, 
            start_date=timezone.now().date()
        )

        if created:
            instance.remaining_lessons += 12
            instance.save()

class ReplacementAttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplacementAttendance
        fields = ['id','attendances','class_instance','date','status']

