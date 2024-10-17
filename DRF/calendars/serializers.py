from rest_framework import serializers
from .models import Calendar
from branches.models import Branch


class CalendarSerializer(serializers.ModelSerializer):
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source='branch'
    )

    class Meta:
        model = Calendar
        fields = ['id', 'title', 'description', 'start_datetime', 'end_datetime', 'year', 'month',
                  'entry_type', 'branch_id', 
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        branch = validated_data.pop('branch')
        calendar = Calendar.objects.create(branch=branch, **validated_data)
        return calendar
