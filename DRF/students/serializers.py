from accounts.serializers import ParentDetailSerializer
from accounts.models import User ,Role , UserProfile , UserAddress
from branches.models import Branch ,UserBranchRole
from classes.models import StudentEnrolment,Class, VideoAssignment
from classes.serializers import StudentEnrolmentDetailsSerializer
from datetime import datetime
from django.db import transaction
from feeStructure.models import Grade,Tier
from rest_framework import serializers

from .models import Students
from payments.service import PaymentService
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
    branch = serializers.SerializerMethodField()
    class Meta:
        model = Students
        fields = [
            'id','first_name','last_name','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date',
            'branch','parent','enrolments','referral_channel','referral','starter_kits'
        ]

    def get_branch(self, obj):
        return obj.branch.display_name
        # read_only_fields = ['branch', 'parent']

class StudentCreateSerializer(serializers.ModelSerializer):
    timeslot = serializers.CharField(write_only=True)
    tier = serializers.CharField(write_only=True)
    start_date = serializers.DateField(write_only=True)
    parent_details = serializers.DictField(write_only=True,required=False)

    class Meta:
        model = Students
        fields = [
            'id','first_name','last_name','fullname','gender','dob',
            'school','tier','deemcee_starting_grade','status','start_date','timeslot','referral_channel','referral','starter_kits',
            'branch','parent','parent_details','created_at','updated_at'
        ]

    def validate_tier(self, value):
        """
        Validate and format tier data
        """
        if isinstance(value, str):
            try:
                return Tier.objects.get(id=value)
            except Tier.DoesNotExist:
                raise serializers.ValidationError("Invalid tier")
        return value

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
    
    def validate(self, data):
        parent = data.get('parent')
        parent_details = data.get('parent_details')
        branch = data.get('branch')

        if not parent and not parent_details:
            raise serializers.ValidationError({
                "parent_details": "Parent details are required when parent is not selected"
            })

        if not parent and parent_details:
            if not isinstance(parent_details, dict):
                raise serializers.ValidationError({
                    "parent_details": "Parent details must be a dictionary"
                })

            required_fields = ['username', 'email']
            missing_fields = [field for field in required_fields if field not in parent_details]
            
            if missing_fields:
                raise serializers.ValidationError({
                    "parent_details": f"Missing required fields: {', '.join(missing_fields)}"
                })

        if parent:
            
            if not User.objects.filter(id=parent.id).exists():
                raise serializers.ValidationError("Invalid Parent ID.")
            
            parent_role = Role.objects.filter(name='parent')
            
            if not parent_role.exists():
                raise serializers.ValidationError("Parent role is not found.Please create a parent role.")
            
            branch = Branch.objects.filter(id=branch.id)
            
            if not branch.exists():
                raise serializers.ValidationError("Branch is not valid for creating a user")

            has_parent_role = UserBranchRole.objects.filter(
                user = parent,
                role = parent_role.first(),
                branch = branch.first()
            ).exists()

            if not has_parent_role:
                raise serializers.ValidationError("The selected user does have a parent role in the speficied branch.")
            
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        timeslot = validated_data.pop('timeslot', None)
        start_date = validated_data.pop('start_date')
        parent_details = validated_data.pop('parent_details', None)
        tier = validated_data.pop('tier', None)

        # Create new parent user if parent_details is provided
        if parent_details and not validated_data.get('parent'):
            branch = validated_data.get('branch')
            
            # Get parent role
            parent_role = Role.objects.filter(name='parent').first()

            if not parent_role:
                raise serializers.ValidationError({
                    "parent": "Parent role is not found. Please create a parent role."
                })

            try:
            # Create new user
                new_parent = User.objects.create(
                    username=parent_details['username'],
                    email=parent_details['email'],
                    password="Password123!",
                    # Add any other required User fields here
                )

                # Create UserBranchRole for the new parent
                UserBranchRole.objects.create(
                    user=new_parent,
                    role=parent_role,
                    branch=branch
                )

                UserProfile.objects.create(
                    user=new_parent)
                
                UserAddress.objects.create(
                    user=new_parent)
                # Set the new parent as the student's parent
                validated_data['parent'] = new_parent

            except Exception as e:
                raise serializers.ValidationError({
                    "parent": f"Error creating parent: {str(e)}"
                })

        student = Students.objects.create(**validated_data)

        if timeslot:
            try:
                class_instance = Class.objects.get(id=timeslot)
                grade = tier.grades.filter(grade_level=student.deemcee_starting_grade).first()
                new_enrolment = StudentEnrolment(
                    student=student,
                    classroom=class_instance,
                    branch=student.branch,
                    grade_id=grade.id,
                    start_date=start_date,
                )
                new_enrolment.save()

                PaymentService.create_payment(
                    enrolment=new_enrolment,
                    amount=grade.price,
                    parent=student.parent,
                    branch=student.branch,
                    enrolment_type="ENROLMENT"
                )

                self._create_video_assignments(new_enrolment)
                
            except Class.DoesNotExist:
                raise serializers.ValidationError({"timeslot": "Invalid class ID provided"})
        
        else:
            raise serializers.ValidationError({"timeslot": "Timeslot is required"})

        return student
    
    def _create_video_assignments(self,enrolment_instance):

        try:
            va_arr = [
                VideoAssignment(enrolment=enrolment_instance, video_number=1),
                VideoAssignment(enrolment=enrolment_instance, video_number=2)
            ]
            VideoAssignment.objects.bulk_create(va_arr)
        except Exception as e:
            raise serializers.ValidationError({"Failed to create video assignments"})

class StudentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Students
        fields = [
            'id','first_name','last_name','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date','referral_channel','referral'
        ]

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)