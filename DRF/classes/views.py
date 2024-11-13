from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.global_customViews import BaseCustomListAPIView ,GenericViewWithExtractJWTInfo, BaseCustomClassView
from accounts.permission import IsManagerOrHigher
from django.db.models import Q

from .models import Class,StudentEnrolment
from .serializers import ClassListSerializer,StudentEnrolmentListSerializer,ClassCreateUpdateSerializer

class ClassListView(BaseCustomListAPIView):
    serializer_class = ClassListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        branch_id = self.request.headers.get('BranchId')
        q = self.request.query_params.get('q', None)
        
        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)
        
        # query_set = User.objects.filter(users__role__name=role).exclude(id=self.request.user.id)
        query_set = Class.objects.filter(branch=int(branch_id))
        
        if q:
            query_set = query_set.filter(
                Q(name=q)  # Case-insensitive search
            )
        if is_superadmin:
            return query_set
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return query_set

class ClassDetailsView(BaseCustomClassView,RetrieveAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassListSerializer
    permission_classes = [IsManagerOrHigher]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class ClassCreateView(GenericViewWithExtractJWTInfo,CreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassCreateUpdateSerializer
    permission_classes = [IsManagerOrHigher]

    def create(self, request, *args, **kwargs):
        branch_id = self.request.headers.get('BranchId')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        if not is_superadmin and not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")
        
        data = request.data.copy()
        data['branch'] = int(branch_id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

class ClassUpdateView(BaseCustomClassView,UpdateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassCreateUpdateSerializer
    permission_classes = [IsManagerOrHigher]

    def update(self, request, *args, **kwargs):
        branch_id = self.request.headers.get("BranchId")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        data['branch'] = int(branch_id)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
    
        self.perform_update(serializer)
        
        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)
        
        return Response({
            "success": True,
            "data": updated_serializer.data
        })
    
class ClassDestroyView(BaseCustomClassView,DestroyAPIView):
    queryset = Class.objects.all()
    permission_classes = [IsManagerOrHigher]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        self.perform_destroy(instance)    
        return Response({"success": True, "message": f"Class {id} deleted successfully"})
    
# Create your views here.

class StudentEnrolmentListView(BaseCustomListAPIView):
    queryset = StudentEnrolment.objects.all()
    serializer_class = StudentEnrolmentListSerializer
    permission_classes = [IsAuthenticated]