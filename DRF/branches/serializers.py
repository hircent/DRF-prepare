from rest_framework import serializers
from .models import Branch

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