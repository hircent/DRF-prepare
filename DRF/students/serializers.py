from accounts.serializers import ParentDetailSerializer
from accounts.models import User ,Role
from branches.models import Branch ,UserBranchRole
from .models import Students
from classes.models import StudentEnrolment,Class
from classes.serializers import StudentEnrolmentDetailsSerializer
from category.models import Grade
from rest_framework import serializers
import json


class StudentListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Students
        fields = [
            'id','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date'
        ]


class StudentDetailsSerializer(serializers.ModelSerializer):
    parent = ParentDetailSerializer()
    enrolments = StudentEnrolmentDetailsSerializer(many=True)

    class Meta:
        model = Students
        fields = [
            'id','first_name','last_name','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date',
            'branch','parent','enrolments'
        ]

        # read_only_fields = ['branch', 'parent']

class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    timeslot = serializers.CharField(write_only=True)

    class Meta:
        model = Students
        fields = [
            'id','first_name','last_name','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date','timeslot','referral_channel','referral','starter_kits',
            'branch','parent','created_at','updated_at'
        ]

    def validate_starter_kits(self, value):
        """
        Validate and format starter_kits data
        """
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for starter_kits")
        return value

    def validate_branch(self,value):
        if value and not Branch.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid Branch ID.")
        return value
    
    def validate_parent(self, value):
        if value:
            
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("Invalid Parent ID.")
            
            parent_role = Role.objects.filter(name='parent')
            
            if not parent_role.exists():
                raise serializers.ValidationError("Parent role is not found.Please create a parent role.")
            
            branch = Branch.objects.filter(id=self.initial_data.get("branch"))
            
            if not branch.exists():
                raise serializers.ValidationError("Branch is not valid for creating a user")

            has_parent_role = UserBranchRole.objects.filter(
                user = value,
                role = parent_role.first(),
                branch = branch.first()
            ).exists()

            if not has_parent_role:
                raise serializers.ValidationError("The selected user does have a parent role in the speficied branch.")
            
        return value
    
    def create(self, validated_data):
        timeslot = validated_data.pop('timeslot',None)

        student = Students.objects.create(**validated_data)

        if timeslot:
            try:
                class_instance = Class.objects.get(id=timeslot)
                
                # Create the enrolment with all required fields
                new_enrolment = StudentEnrolment(
                    student=student,
                    classroom=class_instance,
                    branch=student.branch,
                    grade=Grade.objects.get(grade_level=student.deemcee_starting_grade),
                    start_date=student.enrolment_date  # Set start_date before saving
                )
                new_enrolment.save()
                
            except Class.DoesNotExist:
                raise serializers.ValidationError({"timeslot": "Invalid class ID provided"})

        return student