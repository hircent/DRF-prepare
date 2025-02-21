from rest_framework import serializers
from .models import Category, Theme, ThemeLesson
from feeStructure.models import Grade

class ThemeLessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeLesson
        fields = ['id', 'title']

class ThemeLessonDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeLesson
        fields = ['id', 'name', 'order']

class ThemeLessonAndNameDetailsSerializer(serializers.ModelSerializer):
    theme = serializers.SerializerMethodField()

    class Meta:
        model = ThemeLesson
        fields = ['id', 'name', 'theme']

    def get_theme(self, obj):
        return obj.theme.name

class ThemeLessonCreateUpdateSerializer(serializers.Serializer):
    lesson_one = serializers.CharField(required=True)
    lesson_two = serializers.CharField(required=True)
    lesson_three = serializers.CharField(required=True)
    lesson_four = serializers.CharField(required=True)

    def validate(self, data):
        """
        Validate that all lesson fields are present and not empty
        """
        for lesson_key in ['lesson_one', 'lesson_two', 'lesson_three', 'lesson_four']:
            if not data.get(lesson_key):
                raise serializers.ValidationError({
                    lesson_key: "This field cannot be empty."
                })
        return data


class ThemeListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    class Meta:
        model = Theme
        fields = ['id', 'name','order','category','year']
    
    def get_category(self,obj):
        return obj.category.label
    
    def get_year(self,obj):
        return obj.category.year

class ThemeDetailsSerializer(serializers.ModelSerializer):
    lessons = ThemeLessonDetailsSerializer(source='theme_lessons', read_only=True,many=True)
    class Meta:
        model = Theme
        fields = ['id', 'name', 'category', 'lessons']
    
class ThemeCreateSerializer(serializers.ModelSerializer):
    lessons = ThemeLessonCreateUpdateSerializer(write_only=True)
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
        
        count = Theme.objects.filter(category=category_instance).count()

        theme = Theme.objects.create(category=category_instance, order=count+1, **validated_data)

        lesson_mappings = {
            'lesson_one': lessons['lesson_one'],
            'lesson_two': lessons['lesson_two'],
            'lesson_three': lessons['lesson_three'],
            'lesson_four': lessons['lesson_four']
        }
        #here we are creating theme lessons
        theme_lessons = [
            ThemeLesson(
                theme=theme,
                name=lesson_value,
                order=idx + 1
            )
            for idx, lesson_value in enumerate(lesson_mappings.values())
        ]

        ThemeLesson.objects.bulk_create(theme_lessons)
        return theme
    
    

class ThemeUpdateSerializer(serializers.ModelSerializer):
    lessons = ThemeLessonCreateUpdateSerializer(write_only=True)
    class Meta:
        model = Theme
        fields = ['id', 'name', 'category', 'lessons']
    
    def update(self, instance, validated_data):
        category = validated_data.pop('category')
        lessons = validated_data.pop('lessons')
        category_instance = Category.objects.get(id=category.id)

        if not category_instance:
            raise serializers.ValidationError("Invalid Category.")
        
        if not lessons:
            raise serializers.ValidationError("Lessons are required.")
        
        # Update theme lessons
        lesson_mappings = {
            'lesson_one': lessons['lesson_one'],
            'lesson_two': lessons['lesson_two'],
            'lesson_three': lessons['lesson_three'],
            'lesson_four': lessons['lesson_four']
        }
        
        # Get existing theme lessons
        existing_lessons = ThemeLesson.objects.filter(theme=instance)
        
        if existing_lessons.exists():
            # Update existing lessons
            for idx, (_, lesson_value) in enumerate(lesson_mappings.items()):
                lesson = existing_lessons[idx]
                lesson.name = lesson_value
                lesson.save()
        else:
            # Create new lessons if none exist
            theme_lessons = [
                ThemeLesson(
                    theme=instance,
                    name=lesson_value,
                    order=idx + 1
                )
                for idx, lesson_value in enumerate(lesson_mappings.values())
            ]
            ThemeLesson.objects.bulk_create(theme_lessons)
        
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
    themes = ThemeListSerializer(many=True, read_only=True)
    
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


