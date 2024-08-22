from .models import Role, User
from .serializers import UserSerializer ,serializers
from rest_framework import generics,status
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

    def list(self, request, *args, **kwargs):
        """Override the list method to customize the response format."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success":True,
            "data": serializer.data
        }
        return Response(response_data)
    
        
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
                    raise serializers.ValidationError({
                        "msg":f"Principals can only assign the following roles: {allowed_roles},you are creating '{role_name}'"
                    })
            
            serializer.save()
        else:
            raise PermissionDenied({
                "msg":"You do not have permission to create users."
            })
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Customize the response format
        response_data = {
            "status": status.HTTP_201_CREATED,
            "success":True,
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    

class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"
