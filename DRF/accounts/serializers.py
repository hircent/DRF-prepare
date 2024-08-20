from rest_framework import serializers
from .models import SuperAdmin

class SuperAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ["id","email","phone_number","username","first_name","last_name","date_joined","last_login"]