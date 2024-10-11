from api.global_customViews import BaseCustomListAPIView , BaseCustomBranchView
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher
from accounts.models import User
from django.db.models import Q

from .serializers import BranchCreateUpdateSerializer,BranchDetailsSerializer,BranchListSerializer,PrincipalAndBranchGradeSerializer
from .models import Branch,UserBranchRole,BranchGrade

from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
# Create your views here.


class BranchListView(BaseCustomListAPIView,generics.ListAPIView):
    serializer_class = BranchListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Branch.objects.all().order_by("id")
        q = self.request.query_params.get('q', None)
        '''
        Branch.objects.filter(Q(name__icontains='hq') | Q(business_name__icontains='hq'))
        '''
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)  # Case-insensitive search
            )
        # Check if user has any superadmin role
        is_superadmin = UserBranchRole.objects.filter(
            user=user,
            role__name='superadmin'  # Adjust based on how you identify the superadmin role
        ).exists()
        
        if not is_superadmin:
            # Get all branch IDs where the user has any role
            user_branch_ids = UserBranchRole.objects.filter(
                user=user
            ).values_list('branch_id', flat=True)
            
            # Filter queryset to only include these branches
            queryset = queryset.filter(id__in=user_branch_ids)
        
        return queryset

class BranchRetrieveView(BaseCustomBranchView,generics.RetrieveAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchDetailsSerializer
    permission_classes = [IsPrincipalOrHigher]
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class BranchCreateView(generics.CreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchCreateUpdateSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
    
class BranchUpdateView(BaseCustomBranchView,generics.UpdateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchCreateUpdateSerializer
    permission_classes = [IsPrincipalOrHigher]

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

    
class BranchDeleteView(BaseCustomBranchView,generics.DestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchCreateUpdateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'branch_id'
    permission_classes = [IsSuperAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        self.perform_destroy(instance)
        return Response({"success": True, "message": f"Branch {id} deleted successfully"})

    
class CombinedPrincipalsAndBranchGradesView(APIView):
    permission_classes = [IsSuperAdmin]
    def get(self, request):
        # Get all principals
        # principals = User.objects.filter(
        #     users__role__name='principal'
        # )

        principals = User.objects.filter(
            users__role__isnull=True
        )
        
        '''
        Should be list out who has no role instead of principal

        principals = User.objects.filter(
            users__role__isnull=True
        )
        '''
        # Get all branch grades
        branch_grades = BranchGrade.objects.all()

        # Combine data
        combined_data = {
            'principals': principals,
            'branch_grades': branch_grades
        }

        # Serialize the combined data
        serializer = PrincipalAndBranchGradeSerializer(combined_data)
        
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)