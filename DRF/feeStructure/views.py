from rest_framework.response import Response
from .models import Tier, Grade
from .serializers import (
    GradeListSerializer, GradeDetailsSerializer, GradeCreateUpdateSerializer, TierListSerializer
)
from accounts.permission import IsSuperAdmin
from api.global_customViews import BaseCustomListAPIView, BaseCustomListNoPaginationAPIView
from branches.models import Branch
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class GradeListView(BaseCustomListNoPaginationAPIView):
    serializer_class = GradeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tier = self.request.query_params.get('tier')
        self.require_query_param(tier,"tier")
    
        return Grade.objects.filter(tier__id=int(tier)).order_by('grade_level')
    
class GradeRetrieveView(generics.RetrieveAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeDetailsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'grade_id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class GradeCreateView(generics.CreateAPIView):
    serializer_class = GradeCreateUpdateSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
    
class GradeUpdateView(generics.UpdateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeCreateUpdateSerializer
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
    lookup_url_kwarg = 'grade_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"success": True, "data": serializer.data})

class GradeDestroyView(generics.DestroyAPIView):
    queryset = Grade.objects.all()
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
    lookup_url_kwarg = 'grade_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Grade deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class TierListView(BaseCustomListNoPaginationAPIView):
    serializer_class = TierListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branchId = self.get_branch_id()

        branch = Branch.objects.get(id=branchId)

        return Tier.objects.filter(country__name=branch.country.name)

        