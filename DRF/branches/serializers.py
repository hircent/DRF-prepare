from rest_framework import serializers
from .models import Branch,UserBranchRole

class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "display_name",
            "business_reg_no",
            "description",
            "operation_date",
            "is_headquaters"
        ]

class UserBranchRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_id = serializers.IntegerField(source='branch.id', read_only=True)

    class Meta:
        model = UserBranchRole
        fields = ['role_name', 'branch_name', 'branch_id']