from accounts.models import User
from accounts.serializers import UserSerializer
from api.pagination import CustomPagination
from branches.models import Branch, UserBranchRole
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied


class GenericViewWithExtractJWTInfo(GenericAPIView):
    def extract_jwt_info(self,info):
        jwt_payload = self.request.auth.payload if self.request.auth else None
        
        if not jwt_payload or info not in jwt_payload:
            raise PermissionDenied("Invalid token or missing branch role information")
        
        return jwt_payload.get(info,[])

class BaseCustomListAPIView(GenericViewWithExtractJWTInfo,ListAPIView):
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
    
class BaseCustomBranchSelectorListView(GenericViewWithExtractJWTInfo,ListAPIView):

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class BaseRoleBasedUserView(GenericViewWithExtractJWTInfo):
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('pk')
        role = self.kwargs.get('role')
        branch_id = self.request.headers.get('BranchId')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        queryset = User.objects.filter(id=user_id, users__role__name=role, users__branch_id=branch_id)
        
        if not is_superadmin and not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")

        return get_object_or_404(queryset)
    
class BaseCustomBranchView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.kwargs.get("branch_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        if is_superadmin:
            # Superadmins can access any user regardless of branch
            return get_object_or_404(Branch,id=branch_id)
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return get_object_or_404(Branch,id=branch_id)

