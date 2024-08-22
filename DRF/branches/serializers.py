from rest_framework import serializers
from .models import Branch

class BranchSerializer(serializers.Serializer):

    class Meta:
        object = Branch
        fields = "__all__"