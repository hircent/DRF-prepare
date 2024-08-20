from django.shortcuts import render
from .models import SuperAdmin
from .serializers import SuperAdminSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
# Create your views here.

class SuperAdminListView(generics.ListAPIView):
    queryset = SuperAdmin.objects.all()
    serializer_class = SuperAdminSerializer
    permission_classes = [AllowAny]
