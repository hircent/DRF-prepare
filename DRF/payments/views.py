from api.global_customViews import BaseCustomListNoPaginationAPIView,BaseCustomListAPIView
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher,IsManagerOrHigher,IsTeacherOrHigher
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView,DestroyAPIView,CreateAPIView
from rest_framework.exceptions import PermissionDenied
from .serializers import PaymentListSerializer,InvoiceListSerializer
from .models import InvoiceSequence,Invoice,Payment

# Create your views here.
class PaymentListView(BaseCustomListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentListSerializer

    def get_queryset(self):
        branch_id = self.get_branch_id()
        status = self.request.query_params.get('status', None)
        
        (is_superadmin,user_branch_roles) = self.branch_accessible(branch_id)

        query_set = Payment.objects.filter(enrolment__branch_id=branch_id)
        
        if status:
            query_set = query_set.filter(status=status)

        return query_set
    
class InvoiceListView(BaseCustomListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceListSerializer

    def get_queryset(self):
        branch_id = self.get_branch_id()
        
        self.branch_accessible(branch_id)

        return Invoice.objects.filter(branch_id=branch_id)


