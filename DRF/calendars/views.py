from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Calendar
from .serializers import CalendarSerializer

# Create your views here.

class CalendarListView(ListAPIView):
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        branch_id = self.request.headers.get('BranchId')
        queryset = Calendar.objects.all()

        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        if year:    
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)

        return queryset.order_by('year', 'month', 'start_date')

class CalendarRetrieveView(RetrieveAPIView):
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'calendar_id'
    queryset = Calendar.objects.all()


