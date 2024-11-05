from rest_framework import serializers
from .models import Category, Theme, Grade, ThemeLesson

class ThemeLessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeLesson
        fields = ['id', 'title']

class ThemeLessonDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeLesson
        fields = ['id', 'title', 'lesson_one', 'lesson_two', 'lesson_three', 'lesson_four']

class ThemeListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    class Meta:
        model = Theme
        fields = ['id', 'name', 'category','year']
    
    def get_category(self,obj):
        return obj.category.name
    
    def get_year(self,obj):
        return obj.category.year

class ThemeDetailsSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    lessons = ThemeLessonDetailsSerializer(source='theme_lessons', read_only=True)
    class Meta:
        model = Theme
        fields = ['id', 'name', 'category', 'lessons']

    def get_category(self, obj):
        return obj.category.label
    
class ThemeCreateUpdateSerializer(serializers.ModelSerializer):
    lessons = ThemeLessonDetailsSerializer(write_only=True)
    class Meta:
        model = Theme
        fields = ['id', 'name', 'category', 'lessons']

    def validate_category(self, value):
        if value and not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid Category.")
        
        max_themes = 12  # You can move this to settings if needed
        current_themes_count = Theme.objects.filter(category=value).count()
        if current_themes_count >= max_themes:
            raise serializers.ValidationError(
                f"Category {value.label} already has maximum number of themes ({max_themes})"
            )
        return value
    
    def create(self, validated_data):
        category = validated_data.pop('category')
        lessons = validated_data.pop('lessons')
        category_instance = Category.objects.get(id=category.id)
        if not category_instance:
            raise serializers.ValidationError("Invalid Category.")
        
        if not lessons:
            raise serializers.ValidationError("Lessons are required.")
        
        theme = Theme.objects.create(category=category_instance, **validated_data)
        ThemeLesson.objects.create(theme=theme, **lessons)
        return theme
    
    def update(self, instance, validated_data):
        category = validated_data.pop('category')
        lessons = validated_data.pop('lessons')
        category_instance = Category.objects.get(id=category.id)

        if not category_instance:
            raise serializers.ValidationError("Invalid Category.")
        
        if not lessons:
            raise serializers.ValidationError("Lessons are required.")
        
        themeLesson , _ = ThemeLesson.objects.get_or_create(theme=instance)

        for key, value in lessons.items():
            setattr(themeLesson, key, value)

        themeLesson.save()
        
        instance = super().update(instance, validated_data)
        instance.category = category_instance
        instance.save()
        return instance 

class CategoryListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'label', 'year', 'is_active']

class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'label', 'year', 'is_active']


class CategoryDetailsSerializer(serializers.ModelSerializer):
    themes = ThemeDetailsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'label', 'year', 'is_active', 'themes']

class GradeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'grade_level', 'category', 'price']

class GradeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'grade_level', 'category', 'price']

class GradeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'grade_level', 'category', 'price']

    def validate(self, data):
        grade_level = data.get('grade_level')
        category = data.get('category')

        if grade_level in [1, 2] and category != 'KIDDOS':
            raise serializers.ValidationError("Grades 1 and 2 must be in Kiddos category")
        elif grade_level in [3, 4] and category != 'KIDS':
            raise serializers.ValidationError("Grades 3 and 4 must be in Kids category")
        elif grade_level in [5, 6] and category != 'SUPERKIDS':
            raise serializers.ValidationError("Grades 5 and 6 must be in Superkids category")

        return data
    
    def create(self, validated_data):
        return Grade.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.save()
        return instance 


