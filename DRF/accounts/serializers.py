from students.models import Students
from classes.serializers import StudentEnrolmentListSerializer
from branches.models import Branch,UserBranchRole
from branches.serializers import UserBranchRoleSerializer
from rest_framework import serializers

from .models import User ,UserProfile,Role,UserAddress


class UserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = [
            'address_line_1',
            'address_line_2',
            'address_line_3',
            'postcode',
            'city',
            'state'
        ]

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
    address = UserAddressSerializer(required=False)
    details = UserProfileSerializer(required=False)
    role = serializers.CharField(write_only=True)
    branch_id =serializers.IntegerField(write_only=True)
    user_branch_roles = UserBranchRoleSerializer(many=True, read_only=True)

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
            "address",
            'role',
            'branch_id',
            'user_branch_roles'
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        branch_id = validated_data.pop('branch_id')
        address_data = validated_data.pop('address',None)
        role = validated_data.pop('role')
        details_data = validated_data.pop('details', None)
        user = User.objects.create_user(**validated_data)
        
        userprofile,_ = UserProfile.objects.get_or_create(user=user)
        useraddress,_ = UserAddress.objects.get_or_create(user=user)

        role_obj = Role.objects.get(name=role)
        branch_obj = Branch.objects.get(id=branch_id)
        UserBranchRole.objects.create(user=user, branch=branch_obj, role=role_obj)

        if details_data:
            for key,value in details_data.items():
                setattr(userprofile,key,value)
            userprofile.save()

        if address_data:
            for key,value in address_data.items():
                setattr(useraddress,key,value)
            useraddress.save()
            
        return user
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details",[])
        address_data = validated_data.pop("address",[])

        instance = super().update(instance,validated_data)

        if details_data:
            detail_data,created =  UserProfile.objects.get_or_create(user=instance)
            for attr, value in details_data.items():
                setattr(detail_data, attr, value)
            detail_data.save()

        if address_data:
            addr_data,created =  UserProfile.objects.get_or_create(user=instance)
            for attr, value in details_data.items():
                setattr(addr_data, attr, value)
            addr_data.save()
        
        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    address = UserAddressSerializer(source='user_address', required=False)
    details = UserProfileSerializer(source='user_profile', required=False)
    user_branch_roles = serializers.SerializerMethodField(read_only=True)

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
            "address",
            "user_branch_roles"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_branch_roles"]
        extra_kwargs = {"password": {"write_only": True}}

    
    def get_user_branch_roles(self, obj):
        user_branch_roles = UserBranchRole.objects.filter(user=obj)
        return UserBranchRoleSerializer(user_branch_roles, many=True).data
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('user_address', {})
        profile_data = validated_data.pop('user_profile', {})
        instance = super().update(instance, validated_data)

        # Update or create the user profile
        profile, created = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        address, created = UserAddress.objects.get_or_create(user=instance)
        for attr, value in address_data.items():
            setattr(address, attr, value)
        address.save()

        return instance
    
class ParentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class StuSerializer(serializers.ModelSerializer):
    enrolments = serializers.SerializerMethodField()
    class Meta:
        model = Students
        fields = [
            'id','fullname','deemcee_starting_grade','status','enrolment_date','enrolments'
        ]

    def get_enrolments(self, obj):
        enrolments = obj.enrolments.filter(is_active=True)
        serializer = StudentEnrolmentListSerializer(enrolments, many=True)
        return serializer.data

class ParentDetailsSerializer(serializers.ModelSerializer):
    address = UserAddressSerializer(source='user_address')
    details = UserProfileSerializer(source='user_profile')
    user_branch_roles = serializers.SerializerMethodField(read_only=True)
    children = StuSerializer(many=True,read_only=True)
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
            "details",
            "address",
            "children",
            "user_branch_roles"
        ]

    
    def get_user_branch_roles(self, obj):
        user_branch_roles = UserBranchRole.objects.filter(user=obj)
        return UserBranchRoleSerializer(user_branch_roles, many=True).data
    