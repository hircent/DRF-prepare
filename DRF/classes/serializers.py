from rest_framework import serializers
from .models import (
    Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
)
from branches.models import Branch
from django.db.models import F,Value
       
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

class StudentEnrolmentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = ['id','start_date','status','remaining_lessons','is_active','freeze_lessons','grade']

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
    student_enrolments = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id','branch','name','label','start_time','end_time','day','student_enrolments']

    def get_student_enrolments(self, obj):
        check_after_week = self.context.get('check_after_week')

        enrolments = obj.enrolments.annotate(
            future_remaining_lessons= F('remaining_lessons') - Value(check_after_week)
        ).filter(
            future_remaining_lessons__gt=0,
            is_active=True
        )

        serializer = StudentEnrolmentListForClassSerializer(enrolments, many=True)


        return serializer.data

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
        attendances = obj.attendances.all()
        serializer = StudentAttendanceListSerializer(attendances, many=True)
        return serializer.data
    

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