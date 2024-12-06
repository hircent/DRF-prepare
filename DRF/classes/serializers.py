from rest_framework import serializers
from .models import Class,StudentEnrolment
from accounts.models import User
from branches.models import Branch
from category.models import Category
       
class StudentEnrolmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = '__all__'
        
class StudentEnrolmentListForClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = ['student','enrollment_date','is_active','remaining_lessons']
        
class ClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id','branch','name','label','start_date','start_time','end_time','day']
        

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
    
    