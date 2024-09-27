from rest_framework import serializers
from .models import Students

from accounts.serializers import UserDetailSerializer,UserProfileSerializer,UserSerializer,ParentDetailSerializer
from branches.serializers import BranchAddressSerializer,BranchDetailsSerializer

class StudentListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Students
        fields = [
            'id','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date'
        ]


class StudentDetailsSerializer(serializers.ModelSerializer):
    parent = ParentDetailSerializer(read_only=True)
    class Meta:
        model = Students
        fields = [
            'id','first_name','last_name','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date',
            'branch','parent','created_at','updated_at'
        ]

        read_only_fields = ['branch', 'parent']

class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Students
        fields = [
            'id','first_name','last_name','fullname','gender','dob',
            'school','deemcee_starting_grade','status','enrolment_date',
            'branch','parent','created_at','updated_at'
        ]

    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)