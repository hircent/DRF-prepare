from branches.models import UserBranchRole
from django.db.models import F
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        # Add more user data as needed
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        # user_branch_roles = UserBranchRole.objects.filter(user=user)
        # token['branch_ids'] = list(user_branch_roles.values_list('branch__id', flat=True).distinct())
        # token['roles'] = list(user_branch_roles.values_list('role__name', flat=True))

        user_branch_roles = UserBranchRole.objects.filter(user=user).annotate(
            country=F('branch__country__name'),
            branchid=F('branch__id'),
            role_name=F('role__name'),
            branch_name=F('branch__name')  # Add this line to get branch name
        ).values('branch_id', 'role_name', 'branch_name','country')  # Include branch_name in values
        
        # Updated format to include branch_name
        token['branch_role'] = [
            {
                "branch_id": item['branch_id'],
                "branch_role": item['role_name'],
                "branch_name": item['branch_name'],  # Add branch name to the output
                "country": item['country']
            } for item in user_branch_roles
        ]
        return token

class PasswordStrengthValidator:
    def __init__(self, min_length=8, min_uppercase=1, min_lowercase=1, min_numbers=1, min_special=1):
        self.min_length = min_length
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_numbers = min_numbers
        self.min_special = min_special

    def validate(self, password):
        errors = []
        if len(password) < self.min_length:
            errors.append(f'Password must be at least {self.min_length} characters long.')
        if len(re.findall(r'[A-Z]', password)) < self.min_uppercase:
            errors.append('Password must contain at least one uppercase letter.')
        if len(re.findall(r'[a-z]', password)) < self.min_lowercase:
            errors.append('Password must contain at least one lowercase letter.')
        if len(re.findall(r'[0-9]', password)) < self.min_numbers:
            errors.append('Password must contain at least one number.')
        if len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', password)) < self.min_special:
            errors.append('Password must contain at least one special character.')
        if errors:
            raise ValidationError(errors)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })

        # Custom password strength validation
        password_validator = PasswordStrengthValidator()
        try:
            password_validator.validate(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })

        # Django's built-in password validation
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })

        return attrs