from rest_framework import serializers
from .models import Tier, Grade

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