from api.global_customViews import GenericViewWithExtractJWTInfo
from accounts.permission import IsTeacherOrHigher ,IsManagerOrHigher
from accounts.models import User
from branches.models import Branch ,UserBranchRole
from django.shortcuts import get_object_or_404
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Students
from .serializers import StudentListSerializer,StudentDetailsSerializer,StudentCreateUpdateSerializer
# Create your views here.

class BasedCustomStudentsView(GenericViewWithExtractJWTInfo):

    def get_queryset(self,*args, **kwargs):
        branch_id = self.kwargs.get('branch_id')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            raise PermissionDenied("Branch not found.")

        if is_superadmin:
            return branch.students.all()
        else:
            if not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return branch.students.all()
            
    def get_object(self):

        branch_id = self.kwargs.get("branch_id")
        student_id = self.kwargs.get("student_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        if is_superadmin:
            # Superadmins can access any user regardless of branch
            return get_object_or_404(Students,id=student_id)
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return get_object_or_404(Students,id=student_id)

class StudentListView(BasedCustomStudentsView,generics.ListAPIView):
    serializer_class = StudentListSerializer
    permission_classes = [IsTeacherOrHigher]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "success":True,
            "data": serializer.data
        }
        return Response(response_data)
        

class StudentDetailsView(BasedCustomStudentsView,generics.RetrieveAPIView):
    queryset = Students
    serializer_class = StudentDetailsSerializer
    permission_classes = [IsTeacherOrHigher]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class StudentCreateView(BasedCustomStudentsView,generics.CreateAPIView):
    queryset = Students
    serializer_class = StudentCreateUpdateSerializer
    permission_classes = [IsManagerOrHigher]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
    
        self.perform_update(serializer)
        
        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)
        
        return Response({
            "success": True,
            "data": updated_serializer.data
        })

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
