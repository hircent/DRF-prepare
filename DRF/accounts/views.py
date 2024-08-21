from .models import Role, User
from .serializers import UserSerializer ,serializers
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.has_superadmin_role():
            return User.objects.all()
        elif user.has_role('principal'):
            return User.objects.filter(roles__name__in=['teacher', 'parent', 'student']).distinct()
        return User.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        roles_data = serializer.validated_data.get('roles', [])

        if len(roles_data) < 1:
            raise serializers.ValidationError("Roles must be provided.")
        
        if user.has_superadmin_role():
            serializer.save()
        elif user.has_role('principal'):
            allowed_roles = ['teacher', 'parent', 'student']

            role_names = [role.name for role in roles_data]
            # Check if any of the provided role names are not allowed
            for role_name in role_names:
                if role_name not in allowed_roles:
                    raise serializers.ValidationError(f"Principals can only assign the following roles: {allowed_roles},you are creating '{role_name}'")
            
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to create users.")