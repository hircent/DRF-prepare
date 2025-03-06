from api.global_customViews import BaseCustomListNoPaginationAPIView,BaseCustomListAPIView
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher,IsManagerOrHigher,IsTeacherOrHigher
from datetime import datetime
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView,DestroyAPIView,CreateAPIView
from rest_framework.exceptions import PermissionDenied

from .serializers import (
    PaymentListSerializer, InvoiceListSerializer, PromoCodeListSerializer
)
from .models import (
    Invoice,Payment,PromoCode
)

# Create your views here.
class PaymentListView(BaseCustomListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentListSerializer

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
        status = self.request.query_params.get('status', None)

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

class PromoCodeListView(BaseCustomListNoPaginationAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PromoCodeListSerializer

    def get_queryset(self):
        branch_id = self.get_branch_id()
        purchase_amount = self.request.query_params.get('purchase_amount')
        self.require_query_param(purchase_amount,'min purchase amount')

        return PromoCode.objects.select_related('branch').filter(
            Q(
                expired_at__gt=datetime.today(),
                for_all_branches=True,
                min_purchase_amount__lte=float(purchase_amount)
            ) |
            Q(
                expired_at__gt=datetime.today(),
                branch_id=int(branch_id),
                min_purchase_amount__lte=float(purchase_amount)
            )
        )