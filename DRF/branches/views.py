from rest_framework import generics
from .serializers import BranchSerializer
from .models import Branch

# Create your views here.
class BranchListView(generics.ListAPIView):
    object = Branch.objects.all()
    serializer_class = BranchSerializer