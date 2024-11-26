from rest_framework import serializers
from .models import Calendar ,CalendarThemeLesson
from branches.models import Branch
from category.models import ThemeLesson,Theme
from category.serializers import ThemeLessonDetailsSerializer,ThemeDetailsSerializer


class CalendarListSerializer(serializers.ModelSerializer):
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source='branch'
    )
    
    year = serializers.SerializerMethodField()

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
    
    def update(self, instance, validated_data):
        validated_data = self._set_year_and_month(validated_data)
        return super().update(instance, validated_data)
    
    def get_year(self, obj):
        # Convert the year to a string
        return str(obj.year)
    
    def _set_year_and_month(self, validated_data):
        start_datetime = validated_data.get('start_datetime')
        if start_datetime:
            validated_data['year'] = start_datetime.year
            validated_data['month'] = start_datetime.month
        return validated_data

class CalendarThemeLessonListSerializer(serializers.ModelSerializer):
    theme_lesson = ThemeLessonDetailsSerializer(read_only=True)
    # theme = ThemeDetailsSerializer(read_only=True)
    theme = serializers.SerializerMethodField()
    class Meta:
        model = CalendarThemeLesson
        fields = ['id', 'theme_lesson', 'theme', 'branch', 'lesson_date', 'day', 'month','year']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_theme(self,obj):
        return obj.theme.name