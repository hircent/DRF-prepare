from rest_framework import generics,status
from rest_framework.response import Response
from .serializers import BranchSerializer
from .models import Branch
from rest_framework.exceptions import PermissionDenied
from accounts.permission import IsSuperAdmin
# Create your views here.
class BranchListView(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin]

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
    
class BranchRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin]