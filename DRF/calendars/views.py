from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from api.global_customViews import BaseCustomCalendarListView
from .models import Calendar
from .serializers import CalendarListSerializer

# Create your views here.

class CalendarListView(BaseCustomCalendarListView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        branch_id = self.request.headers.get('BranchId')
        queryset = Calendar.objects.all()

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)
        
        if year:    
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)

        if is_superadmin:
            return queryset.filter(branch_id=branch_id).distinct()
        else:
            
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return queryset.filter(branch_id=branch_id)

class CalendarRetrieveView(RetrieveAPIView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'calendar_id'
    queryset = Calendar.objects.all()


