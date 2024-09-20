from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from accounts.models import User
from accounts.serializers import UserSerializer

class BaseCustomListAPIView(ListAPIView):
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "success":True,
            "data": serializer.data
        }
        return Response(response_data)
    
    def extract_jwt_info(self,info):
        jwt_payload = self.request.auth.payload if self.request.auth else None
        
        if not jwt_payload or 'branch_role' not in jwt_payload:
            raise PermissionDenied("Invalid token or missing branch role information")
        
        return jwt_payload.get(info,[])

class BaseRoleBasedUserView(GenericAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('pk')
        role = self.kwargs.get('role')
        branch_id = self.kwargs.get('branch_id')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        queryset = User.objects.filter(id=user_id, users__role__name=role, users__branch_id=branch_id)

        if not is_superadmin and not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")

        return get_object_or_404(queryset)

    def extract_jwt_info(self, info):
        jwt_payload = self.request.auth.payload if self.request.auth else None
        if not jwt_payload or 'branch_role' not in jwt_payload:
            raise PermissionDenied("Invalid token or missing branch role information")
        return jwt_payload.get(info, [])