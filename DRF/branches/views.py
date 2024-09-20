from rest_framework import generics,status
from rest_framework.response import Response
from .serializers import BranchSerializer
from .models import Branch
from rest_framework.exceptions import PermissionDenied
from accounts.permission import IsSuperAdmin
from api.global_customViews import BaseCustomListAPIView
# Create your views here.

class BranchListView(BaseCustomListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin]


class BranchCreateView(generics.CreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin]
    
class BranchRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin]
    
