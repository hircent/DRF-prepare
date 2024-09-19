from .models import User
from .serializers import UserSerializer ,serializers
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .permission import IsSuperAdmin,IsPrincipalOrHigher,IsManagerOrHigher,IsTeacherOrHigher,IsParentOrHigher
# Create your views here.

class BaseCustomListAPIView(generics.ListAPIView):
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "success":True,
            "data": serializer.data
        }
        return Response(response_data)
    
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
            return query_set.filter(users__branch_id=branch_id)
        else:
            if not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return query_set.filter(users__branch_id=branch_id)
    
    def get_permissions(self):
        permissions = []
        role = self.kwargs.get('role')
        if role == 'superadmin':
            permissions = [IsSuperAdmin()]
        elif role == 'principal':
            permissions = [IsPrincipalOrHigher()]
        elif role == 'manager':
            permissions = [IsManagerOrHigher()]
        elif role == 'teacher':
            permissions = [IsTeacherOrHigher()]
        elif role == 'parent':
            permissions = [IsParentOrHigher()]
        return permissions
    
    def extract_jwt_info(self,info):
        jwt_payload = self.request.auth.payload if self.request.auth else None
        
        if not jwt_payload or 'branch_role' not in jwt_payload:
            raise PermissionDenied("Invalid token or missing branch role information")
        
        return jwt_payload.get(info,[])