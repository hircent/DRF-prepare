
from api.global_customViews import (
    BaseCustomListAPIView,BaseRoleBasedUserView,BaseRoleBasedUserDetailsView,
    BaseCustomParentView,BaseCustomListNoPaginationAPIView
)
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher,IsManagerOrHigher,IsTeacherOrHigher
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import DestroyAPIView,UpdateAPIView,CreateAPIView,RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import User
from branches.models import UserBranchRole
from .serializers import (
    UserSerializer,UserDetailSerializer,ParentDetailsSerializer,
    TeachingUserSerializer,SearchParentSerializer
)
# Create your views here.
    
class RoleBasesUserListView(BaseCustomListAPIView):
    serializer_class = UserSerializer
    def get_queryset(self):    
        role = self.kwargs.get('role')
        q = self.request.query_params.get('q', None)
        
        branch_id = self.get_branch_id()
        (is_superadmin,user_branch_roles) = self.branch_accessible(branch_id)
        
        # query_set = User.objects.filter(users__role__name=role).exclude(id=self.request.user.id)
        query_set = User.objects.filter(users__role__name=role,users__branch_id=branch_id)
        
        if q:
            query_set = query_set.filter(
                Q(username__icontains=q)  # Case-insensitive search
            )
        if is_superadmin:
            if role == 'superadmin':
                return query_set
            else:
                return query_set.distinct()
        else:
            
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return query_set
            
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsPrincipalOrHigher],
            'manager': [IsManagerOrHigher],
            'teacher': [IsTeacherOrHigher],
            'parent': [IsTeacherOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]

class RoleBasedUserCreateView(BaseRoleBasedUserView, CreateAPIView):
    def create(self, request, *args, **kwargs):
        role = self.kwargs.get('role')
        branch_id = self.get_branch_id()
        (is_superadmin,user_branch_roles) = self.branch_accessible(branch_id)

        data = request.data.copy()
        data['role'] = role
        data['branch_id'] = branch_id
        if 'details' in request.data:
            data['details'] = request.data.get('details')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()
    
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsSuperAdmin],
            'manager': [IsPrincipalOrHigher],
            'teacher': [IsManagerOrHigher],
            'parent': [IsManagerOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]
    
class RoleBasedUserUpdateView(BaseRoleBasedUserView,UpdateAPIView):
    serializer_class = UserDetailSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "msg": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)

        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)
        
        return Response({
            "success": True,
            "data": updated_serializer.data
        })
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsPrincipalOrHigher],
            'manager': [IsManagerOrHigher],
            'teacher': [IsTeacherOrHigher],
            'parent': [IsManagerOrHigher]
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
            'parent': [IsManagerOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]

class RoleBasedUserDetailsView(BaseRoleBasedUserDetailsView,RetrieveAPIView):
    serializer_class = UserDetailSerializer  # Assuming this includes UserProfile data
    queryset = User.objects.all()
    
    def get_object(self):
        # Get the user object by ID
        user_id = self.kwargs.get('pk')  # 'pk' corresponds to the user ID in the URL

        # You can add permission checks here based on user roles
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        user = get_object_or_404(User, id=user_id)
        '''
        # Extract user roles from JWT
        user_branch_roles = self.extract_jwt_info("branch_role")
        
        # Check if the user is a superadmin
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        # Fetch the user
        user = get_object_or_404(User, id=user_id)
        
        if is_superadmin:
            # Superadmins can access any user regardless of branch
            return user
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=user, branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return user
        '''
        user_branch_role = UserBranchRole.objects.filter(user=user, branch_id=branch_id).first()
        
        if not user_branch_role:
            raise PermissionDenied("The requested user does not belong to the specified branch.")
        return user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)  # Serialize the user instance
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    def get_permissions(self):
        role = self.kwargs.get('role')
        permission_classes = {
            'superadmin': [IsSuperAdmin],
            'principal': [IsPrincipalOrHigher],
            'manager': [IsManagerOrHigher],
            'teacher': [IsTeacherOrHigher],
            'parent': [IsTeacherOrHigher]
        }
        return [permission() for permission in permission_classes.get(role, [])]
    

'''
ParentViews

'''



class ParentListView(BaseCustomListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsTeacherOrHigher]
    
    def get_queryset(self):    
        q = self.request.query_params.get('q', None)
        
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
        # query_set = User.objects.filter(users__role__name=role).exclude(id=self.request.user.id)
        query_set = User.objects.filter(users__role__name='parent',users__branch_id=branch_id)
        
        if q:
            query_set = query_set.filter(
                Q(username__icontains=q)  # Case-insensitive search
            )
        return query_set
            
class ParentDetailsView(BaseCustomParentView,RetrieveAPIView):
    serializer_class = ParentDetailsSerializer
    permission_classes = [IsTeacherOrHigher]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class TeachingUserListView(BaseCustomListNoPaginationAPIView):
    serializer_class = TeachingUserSerializer
    permission_classes = [IsTeacherOrHigher]

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
        query_set = User.objects.filter(
            users__role__name__in=['teacher','manager'],
            users__branch_id=branch_id
        )

        return query_set
    
class SearchParentListView(BaseCustomListNoPaginationAPIView):
    serializer_class = SearchParentSerializer
    permission_classes = [IsTeacherOrHigher]

    def get_queryset(self):
        q = self.request.query_params.get('q', None)
        
        if not q:
            raise PermissionDenied("Missing search query.")
        
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
        query_set = User.objects.filter(
            users__role__name='parent',
            users__branch_id=branch_id
        )

        if q:
            query_set = query_set.filter(
                Q(email__icontains=q)  # Case-insensitive search
            )

        return query_set