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
    students = serializers.SerializerMethodField()
    class Meta:
        model = Class
        fields = ['id','branch','category','name','label','description','start_time','end_time','day','students']
        
    def get_students(self, obj):
        # Get all StudentEnrolment instances for this class
        enrolments = StudentEnrolment.objects.filter(class_instance=obj).order_by('student__last_name')
        return StudentEnrolmentListForClassSerializer(enrolments, many=True).data

class ClassCreateUpdateSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        error_messages={
            'does_not_exist': 'Invalid Branch.',
        }
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={
            'does_not_exist': 'Invalid Category.',
        }
    )
    class Meta:
        model = Class
        fields = [
            'id',
            'branch',
            'category',
            'name',
            'label',
            'description',
            'start_time',
            'end_time',
            'day',
        ]

    def create(self, validated_data):
        # Pop the branch and category data from the validated data
        branch_data = validated_data.pop("branch", None)
        category_data = validated_data.pop("category", None)
        
        branch_data = Branch.objects.get(id=branch_data.id)
        category_data = Category.objects.get(id=category_data.id)
        # Create the class instance
        class_instance = Class.objects.create(branch=branch_data, category=category_data, **validated_data)

        return class_instance
    
    