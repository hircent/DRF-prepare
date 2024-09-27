from accounts.serializers import ParentDetailSerializer
from accounts.models import User ,Role
from branches.models import Branch ,UserBranchRole
from .models import Students

from rest_framework import serializers


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