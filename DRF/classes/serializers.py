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
    class Meta:
        model = StudentEnrolment
        fields = ['student','is_active','remaining_lessons']
        
class ClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id','branch','name','label','start_date','start_time','end_time','day']
        
class ClassEnrolmentListSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id','branch','name','label','start_time','end_time','day','students']

    def get_students(self, obj):
        check_after_week = self.context.get('check_after_week')

        enrolments = obj.enrolments.annotate(
            future_remaining_lessons= F('remaining_lessons') - Value(check_after_week)
        ).filter(
            future_remaining_lessons__gt=13
        )

        # for enrolment in enrolments:
        #     print("=======================================================")
        #     print(enrolment.student.fullname)
        #     print(enrolment.remaining_lessons)
        #     print(enrolment.future_remaining_lessons)
        #     print("=======================================================")

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
    
    