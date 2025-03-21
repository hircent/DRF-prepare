from api.global_customViews import (
    BaseCustomListNoPaginationAPIView, BaseCustomListAPIView, BasePromoCodeView, BasePaymentView
)
from accounts.permission import IsSuperAdmin,IsPrincipalOrHigher,IsManagerOrHigher,IsTeacherOrHigher
from branches.models import Branch
from classes.models import StudentAttendance
from datetime import datetime
from django.db.models import Q,Count,Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView,DestroyAPIView,CreateAPIView,RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from students.models import Students

from .serializers import (
    PaymentListSerializer, InvoiceListSerializer, PromoCodeSerializer, PromoCodeCreateUpdateSerializer,
    PaymentDetailsSerializer, PaymentReportListSerializer
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
        query_set = Payment.objects.filter(start_date__year=2025,start_date__month=1,enrolment__branch_id=branch_id).select_related('enrolment','enrolment__student','enrolment__grade')
        
        if status:
            query_set = query_set.filter(status=status)

        return query_set
    
class PaymentReportListView(BaseCustomListNoPaginationAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentReportListSerializer

    def get_queryset(self,year,month):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
        query_set = Payment.objects.filter(
            start_date__year=year,start_date__month=month,enrolment__branch_id=branch_id
        ).select_related(
            'enrolment','enrolment__student','enrolment__grade'
        )

        return query_set
    
    def list(self, request, *args, **kwargs):
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        today = datetime.today()

        if not month:
            month = today.month

        if not year:
            year = today.year

        queryset = self.get_queryset(year,month)

        branch_id = self.get_branch_id()

        students = Students.objects.filter(branch_id=branch_id).aggregate(
            total=Count('id'),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            dropped_out=Count('id', filter=Q(status='DROPPED_OUT')),
            graduated=Count('id', filter=Q(status='GRADUATED'))
        )

        attendances = StudentAttendance.objects.filter(
            branch_id=branch_id,date__year=year,date__month=month
        ).aggregate(
            absent=Count('id', filter=Q(status='ABSENT')),
            freeze=Count('id', filter=Q(status='FREEZED')),
            sfreezed=Count('id', filter=Q(status='SFREEZED')),
            replacement=Count('id', filter=Q(status='REPLACEMENT'))
        )

        branch:Branch = Branch.objects.select_related('branch_grade','country').get(id=branch_id)

        total_paid_amount = Payment.objects.filter(
            start_date__year=year,start_date__month=month,enrolment__branch_id=branch_id
        ).aggregate(total=Sum('amount') - Sum('discount'))['total'] or 0

        payment_serializer = self.get_serializer(queryset, many=True)
        percentage = branch.branch_grade.percentage

        paid_amount_formatted = "{:.2f}".format(float(total_paid_amount))
        loyalty_fees = "{:.2f}".format(float(total_paid_amount) * (percentage / 100))

        return Response({
            "success": True,
            "data": {
                "total_payments": len(payment_serializer.data),
                "payments": payment_serializer.data,
                "student_info":students,
                "branch_info": {
                    'branch_grade': branch.branch_grade.name,
                    'branch_percentage': percentage,
                    'country_code': branch.country.code 
                },
                "attendances":attendances,
                "total_paid_amount":paid_amount_formatted,
                "loyalty_fees":loyalty_fees
            }
        })
    
class PaymentDetailsView(BasePaymentView,RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentDetailsSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class InvoiceListView(BaseCustomListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceListSerializer

    def get_queryset(self):
        branch_id = self.get_branch_id()
        
        self.branch_accessible(branch_id)

        return Invoice.objects.filter(branch_id=branch_id)

class PromoCodeListView(BaseCustomListNoPaginationAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PromoCodeSerializer

    def get_queryset(self):

        branch = self.request.query_params.get('branch')

        if branch:
            return PromoCode.objects.filter(branch_id=int(branch))
        
        return PromoCode.objects.all()
    
class PromoCodeListForPaymentView(BaseCustomListNoPaginationAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PromoCodeSerializer

    def get_queryset(self):
        branch_id = self.get_branch_id()
        purchase_amount = self.request.query_params.get('purchase_amount')
        # self.require_query_param(purchase_amount,'min purchase amount')

        return PromoCode.objects.select_related('branch').filter(
            Q(
                expired_at__gt=datetime.today(),
                for_all_branches=True,
                # min_purchase_amount__lte=float(purchase_amount)
            ) |
            Q(
                expired_at__gt=datetime.today(),
                branch_id=int(branch_id),
                # min_purchase_amount__lte=float(purchase_amount)
            )
        )
    
class PromoCodeDetailsView(BasePromoCodeView,RetrieveAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PromoCodeSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class PromoCodeCreateView(BasePromoCodeView,CreateAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PromoCodeCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

class PromoCodeUpdateView(BasePromoCodeView,UpdateAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PromoCodeCreateUpdateSerializer

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

class PromoCodeDeleteView(BasePromoCodeView,DestroyAPIView):
    permission_classes = [IsSuperAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        self.perform_destroy(instance)    
        return Response({"success": True, "message": f"Promo Code {id} deleted successfully"})
    