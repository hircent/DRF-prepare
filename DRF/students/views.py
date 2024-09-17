from rest_framework import generics,status
from rest_framework.response import Response
from .models import Students
from .serializers import StudentSerializer
from rest_framework.permissions import AllowAny
# Create your views here.

class StudentListView(generics.ListAPIView):
    queryset = Students.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):

        print(request.user)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success":True,
            "data": serializer.data
        }
        return Response(response_data)