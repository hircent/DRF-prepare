from api.global_customViews import BaseCustomListNoPaginationAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Country
from .serializers import CountryListSerializer

# Create your views here.
class CountryListView(BaseCustomListNoPaginationAPIView):
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer
    permission_classes = [IsAuthenticated]
