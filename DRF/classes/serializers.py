from rest_framework import serializers
from .models import Class,StudentEnrolment
from accounts.models import User
from branches.models import Branch
from category.models import Category

from django.db.models import F,Value
       
class StudentEnrolmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = '__all__'
        
class StudentEnrolmentListForClassSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    future_remaining_lessons = serializers.IntegerField(read_only=True)

    class Meta:
        model = StudentEnrolment
        fields = ['id', 'student','is_active','future_remaining_lessons']

    def get_student(self, obj):
        return { "id": obj.student.id, "fullname": obj.student.fullname }
        
class ClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id','branch','name','label','start_date','start_time','end_time','day']
        
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
    
    