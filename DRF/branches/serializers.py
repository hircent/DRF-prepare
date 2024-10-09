from rest_framework import serializers
from .models import Branch,UserBranchRole,BranchAddress,BranchGrade
from accounts.models import User,Role

class BranchGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchGrade  # Assuming your model is named BranchGrade
        fields = ['id', 'name']

class BranchAddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BranchAddress
        fields = ["address_line_1","address_line_2","address_line_3","postcode","city","state","created_at","updated_at"]
        
class BranchListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = [
            'id','branch_grade','name','display_name','business_reg_no',
            'operation_date'
        ]

class BranchCreateUpdateSerializer(serializers.ModelSerializer):
    address = BranchAddressSerializer(source="branch_address", required=False)
    principal = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Branch
        fields = [
            'principal','id', 'branch_grade', 'name', 'display_name', 'business_name', 'business_reg_no',
            'description', 'operation_date', 'is_headquaters', 'created_at', 'updated_at', 'terminated_at', 'address'
        ]

    def validate_branch_grade(self, value):
        if value and not BranchGrade.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid Branch Grade.")
        return value
    
    def validate_principal(self,value):
        if value:
            # Check if user is active
            if not value.is_active:
                raise serializers.ValidationError("User is not active.")
            
            # Get the current instance if this is an update operation
            instance = getattr(self, 'instance', None)
            
            # Check if the user has any existing roles
            existing_roles = UserBranchRole.objects.filter(user=value)
            
            # If this is an update, exclude the current branch's roles from the check
            if instance:
                existing_roles = existing_roles.exclude(branch=instance)
            
            if existing_roles.exists():
                raise serializers.ValidationError("User already has a role in another branch.")
        
        return value

    def create(self, validated_data):
        # Pop the address data from the validated data
        address_data = validated_data.pop("branch_address", None)
        principal_user = validated_data.pop("principal", None)
        
        # Create the branch instance
        branch = Branch.objects.create(**validated_data)

        # If address data is provided, create the BranchAddress
        if address_data:
            BranchAddress.objects.create(branch=branch, **address_data)

        if principal_user:
            principal_role = Role.objects.get(name='principal')
            UserBranchRole.objects.create(
                user=principal_user,
                branch=branch,
                role=principal_role
            )

        return branch

    def update(self, instance, validated_data):
        # Pop the address data and principal from the validated data
        address_data = validated_data.pop("branch_address", None)
        principal_user = validated_data.pop("principal", None)
        
        # Update the branch instance with the non-address fields
        instance = super().update(instance, validated_data)

        # If address data is provided, update or create the BranchAddress
        if address_data:
            # Get or create the BranchAddress associated with this branch
            branch_address, created = BranchAddress.objects.get_or_create(branch=instance)

            # Update the BranchAddress with the new address data
            for key, value in address_data.items():
                setattr(branch_address, key, value)

            # Save the updated BranchAddress
            branch_address.save()

        '''
        defaults={'user': principal_user}
        If a matching object is found, it updates the 'user' field to the new principal_user
        If no matching object is found, it creates a new one with all the parameters (branch, role, and user)
        '''
        # Handle principal update
        if principal_user:
            principal_role = Role.objects.get(name='principal')
            
            # Update or create the UserBranchRole for principal
            user_branch_role, created = UserBranchRole.objects.update_or_create(
                branch=instance,
                role=principal_role,
                defaults={'user': principal_user}
            )

        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Add principal information to the response
        principal_role = instance.user_branch.filter(role__name='principal').first()
        if principal_role:
            representation['principal'] = principal_role.user.id
        
        return representation

        
class BranchDetailsSerializer(serializers.ModelSerializer):
    address = BranchAddressSerializer(source='branch_address',read_only=True)
    principal = serializers.SerializerMethodField()
    branch_grade = BranchGradeSerializer(read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'principal','branch_grade','id','name','display_name','business_name','business_reg_no',
            'description','operation_date','is_headquaters','created_at','created_at',
            'updated_at','terminated_at','address'
        ]

    def get_principal(self,obj):
        try:
            principal_role = UserBranchRole.objects.filter(branch=obj,role__name="principal").select_related('user').first()

            if principal_role:
                return {
                    'id':principal_role.user.id,
                    'username':principal_role.user.username
                }
        except UserBranchRole.DoesNotExist:
            pass

        return None

class UserBranchRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_id = serializers.IntegerField(source='branch.id', read_only=True)

    class Meta:
        model = UserBranchRole
        fields = ['role_name', 'branch_name', 'branch_id']


class PrincipalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username']

class PrincipalAndBranchGradeSerializer(serializers.Serializer):
    principals = PrincipalSerializer(many=True)
    branch_grades = BranchGradeSerializer(many=True)