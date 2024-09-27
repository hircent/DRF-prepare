from api.global_customViews import BaseCustomListAPIView , BaseCustomBranchView
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher

from .serializers import BranchCreateUpdateSerializer,BranchDetailsSerializer,BranchListSerializer
from .models import Branch

from rest_framework import generics,status
from rest_framework.response import Response
# Create your views here.


class BranchListView(BaseCustomListAPIView,generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchListSerializer
    permission_classes = [IsSuperAdmin]

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
    

    
