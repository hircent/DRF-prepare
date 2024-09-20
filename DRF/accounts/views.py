
from api.global_customViews import BaseCustomListAPIView,BaseRoleBasedUserView
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher,IsManagerOrHigher,IsTeacherOrHigher,IsParentOrHigher
from branches.models import Branch ,UserBranchRole

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import DestroyAPIView,UpdateAPIView,CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import User ,Role
from .serializers import UserSerializer
# Create your views here.
    
class RoleBasesUserListView(BaseCustomListAPIView):
    serializer_class = UserSerializer
    def get_queryset(self):    
        role = self.kwargs.get('role')
        branch_id = self.kwargs.get('branch_id')
        
        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)
        
        query_set = User.objects.filter(users__role__name=role)
        
        if is_superadmin:
            if role == 'superadmin':
                return query_set
            else:
                return query_set.filter(users__branch_id=branch_id).distinct()
        else:
            if not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return query_set.filter(users__branch_id=branch_id)
            
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsPrincipalOrHigher],
            'manager': [IsManagerOrHigher],
            'teacher': [IsTeacherOrHigher],
            'parent': [IsParentOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]

class RoleBasedUserCreateView(BaseRoleBasedUserView, CreateAPIView):
    def create(self, request, *args, **kwargs):
        role = self.kwargs.get('role')
        branch_id = self.kwargs.get('branch_id')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        if not is_superadmin and not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        role = self.kwargs.get('role')
        branch_id = self.kwargs.get('branch_id')
        role_obj = Role.objects.get(name=role)  # Fetch the Role object
        branch_obj = Branch.objects.get(id=branch_id)  # Fetch the Branch object

        # Save the user with the related role and branch
        user = serializer.save()  # Save the basic user data
        # Now, link the user to the role and branch
        UserBranchRole.objects.create(user=user,branch=branch_obj,role=role_obj)
    
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsSuperAdmin],
            'manager': [IsPrincipalOrHigher],
            'teacher': [IsManagerOrHigher],
            'parent': [IsTeacherOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]
    
class RoleBasedUserUpdateView(BaseRoleBasedUserView,UpdateAPIView):
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"success": True, "data": serializer.data})
    
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsPrincipalOrHigher],
            'manager': [IsManagerOrHigher],
            'teacher': [IsTeacherOrHigher],
            'parent': [IsParentOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]


class RoleBasedUserDeleteView(BaseRoleBasedUserView,DestroyAPIView):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "User deleted successfully"})
    
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsSuperAdmin],
            'manager': [IsPrincipalOrHigher],
            'teacher': [IsManagerOrHigher],
            'parent': [IsTeacherOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]