from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils import timezone
from django.db.models import Count

from accounts.models import User
from branches.models import UserBranchRole

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise AuthenticationFailed('Token contained no recognizable user identification')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        if user.is_active:
            raise AuthenticationFailed('User is inactive')

        # Check user roles
        user_roles = UserBranchRole.objects.filter(user=user).values('role__name').annotate(role_count=Count('role__name'))
        print(user_roles)
        if user_roles.count() == 1 and user_roles[0]['role__name'] == 'parent' and user_roles[0]['role_count'] == 1:
            raise AuthenticationFailed('User with only parent role cannot log in')

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user