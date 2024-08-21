from rest_framework import serializers
from .models import User ,Role

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all())

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "roles",
            "created_at"
        ]
        extra_kwargs = {"password":{"write_only":True}}

    def create(self, validated_data):

        roles = validated_data.pop('roles', [])
        user = User.objects.create_user(**validated_data)
        user.roles.set(roles)
        user.save()
        return user