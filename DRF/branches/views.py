from rest_framework import generics,status
from rest_framework.response import Response
from .serializers import BranchCreateUpdateSerializer,BranchDetailsSerializer,BranchListSerializer
from .models import Branch
from rest_framework.exceptions import PermissionDenied
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher
# Create your views here.


class BranchListView(generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchListSerializer
    permission_classes = [IsSuperAdmin]

class BranchRetrieveView(generics.RetrieveAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchDetailsSerializer
    permission_classes = [IsPrincipalOrHigher]
    
    def get_object(self,*args, **kwargs):
        pk = self.kwargs.get("pk")
        pass
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class BranchCreateView(generics.CreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchCreateUpdateSerializer
    permission_classes = [IsSuperAdmin]
    
class BranchUpdateView(generics.UpdateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchCreateUpdateSerializer
    permission_classes = [IsPrincipalOrHigher]
    
class BranchDeleteView(generics.DestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchCreateUpdateSerializer
    permission_classes = [IsSuperAdmin]
    

    
