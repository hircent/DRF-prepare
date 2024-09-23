from rest_framework import serializers
from .models import User ,UserProfile,Role
from branches.models import Branch,UserBranchRole
from branches.serializers import UserBranchRoleSerializer

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'gender',
            'dob',
            'ic_number',
            'occupation',
            'spouse_name',
            'spouse_phone',
            'spouse_occupation',
            'no_of_children',
            'personal_email',
            'bank_name',
            'bank_account_name',
            'bank_account_number'
        ]

class UserSerializer(serializers.ModelSerializer):
    details = UserProfileSerializer(required=False)
    role = serializers.CharField(write_only=True)
    branch_id =serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
            "created_at",
            "updated_at",
            "details",
            'role',
            'branch_id'
        ]
        extra_kwargs = {"password":{"write_only":True}}

    def create(self, validated_data):
        branch_id = validated_data.pop('branch_id')
        role = validated_data.pop('role')
        details_data = validated_data.pop('details', None)
        user = User.objects.create_user(**validated_data)
        
        userprofile,_ = UserProfile.objects.get_or_create(user=user)

        role_obj = Role.objects.get(name=role)
        branch_obj = Branch.objects.get(id=branch_id)
        UserBranchRole.objects.create(user=user, branch=branch_obj, role=role_obj)

        if details_data:
            for key,value in details_data.items():
                setattr(userprofile,key,value)
            userprofile.save()
            
        return user
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details",[])

        instance = super().update(instance,validated_data)

        if details_data:
            detail_data,created =  UserProfile.objects.get_or_create(user=instance)
            for attr, value in details_data.items():
                setattr(detail_data, attr, value)
            detail_data.save()
        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    details = UserProfileSerializer(source='user_profile', read_only=True)
    user_branch_roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
            "created_at",
            "updated_at",
            "details",
            "user_branch_roles"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    
    def get_user_branch_roles(self, obj):
        user_branch_roles = UserBranchRole.objects.filter(user=obj)
        return UserBranchRoleSerializer(user_branch_roles, many=True).data