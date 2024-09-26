from rest_framework import serializers
from .models import Branch,UserBranchRole,BranchAddress,BranchGrade

class BranchAddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BranchAddress
        fields = '__all__'
        
class BranchListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = [
            'id','branch_grade','name','display_name','business_reg_no',
            'operation_date'
        ]

class BranchCreateUpdateSerializer(serializers.ModelSerializer):
    address = BranchAddressSerializer(source="branch_address",required=False)
    
    class Meta:
        model = Branch
        fields = [
            'id','branch_grade','name','display_name','business_name','business_reg_no',
            'description','operation_date','is_headquaters','created_at','created_at',
            'updated_at','terminated_at','address'
        ]

    def validate_branch_grade(self,value):
        if value and not BranchGrade.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid Branch Grade.")
        return value
        
    def create(self, validated_data):
        
        address = validated_data.pop("address",[])
        
        branch = Branch.objects.create(**validated_data)
        
        for data in address:
            BranchAddress.objects.create(branch=branch,**data)
            
        return branch
    
    def update(self, instance, validated_data):
        address = validated_data.pop("address",[])
        
        instance = super().update(instance,validated_data)
        
        if address:
            branch_add, _ = BranchAddress.objects.get_or_create(branch=instance)
            
            for key,value in branch_add.items():
                setattr(branch_add,key,value)
            branch_add.save()
        
        return instance
        
class BranchDetailsSerializer(serializers.ModelSerializer):
    address = BranchAddressSerializer(source='branch_address',read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'id','branch_grade','name','display_name','business_name','business_reg_no',
            'description','operation_date','is_headquaters','created_at','created_at',
            'updated_at','terminated_at','address'
        ]

class UserBranchRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_id = serializers.IntegerField(source='branch.id', read_only=True)

    class Meta:
        model = UserBranchRole
        fields = ['role_name', 'branch_name', 'branch_id']