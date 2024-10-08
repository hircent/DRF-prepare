from rest_framework import serializers
from .models import Branch,UserBranchRole,BranchAddress,BranchGrade
from accounts.models import User

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
    
    class Meta:
        model = Branch
        fields = [
            'id', 'branch_grade', 'name', 'display_name', 'business_name', 'business_reg_no',
            'description', 'operation_date', 'is_headquaters', 'created_at', 'updated_at', 'terminated_at', 'address'
        ]

    def validate_branch_grade(self, value):
        if value and not BranchGrade.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid Branch Grade.")
        return value

    def create(self, validated_data):
        # Pop the address data from the validated data
        address_data = validated_data.pop("branch_address", None)
        
        # Create the branch instance
        branch = Branch.objects.create(**validated_data)

        # If address data is provided, create the BranchAddress
        if address_data:
            BranchAddress.objects.create(branch=branch, **address_data)

        return branch

    def update(self, instance, validated_data):
        # Pop the address data from the validated data
        address_data = validated_data.pop("branch_address", None)
        
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

        return instance

        
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