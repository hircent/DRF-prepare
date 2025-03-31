from api.global_customViews import (
    BaseCustomListNoPaginationAPIView, BaseCustomListAPIView, BasePromoCodeView, BasePaymentView
)
from api.mixins import UtilsMixin
from accounts.permission import IsSuperAdmin,IsManagerOrHigher
from branches.models import Branch
from branches.serializers import BranchListReportSerializer
from country.models import Country
from datetime import datetime
from django.db.models import Q
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView,DestroyAPIView,CreateAPIView,RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from reports.service import PaymentReportService

from .serializers import (
    PaymentListSerializer, InvoiceListSerializer, PromoCodeSerializer, PromoCodeCreateUpdateSerializer,
    PaymentDetailsSerializer, PaymentReportListSerializer, MakePaymentSerializer
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
    
class PaymentReportListView(BaseCustomListNoPaginationAPIView,UtilsMixin):
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
        month = self.request.query_params.get('month')
        self.require_query_param(month,'month')
        year = self.request.query_params.get('year')
        self.require_query_param(year,'year')

        queryset = self.get_queryset(year,month)

        branch_id = self.get_branch_id()

        students = PaymentReportService.get_student_statuses(branch_id)
        attendances = PaymentReportService.get_attendance_statuses(year,month,branch_id)

        (total_amount,total_discount,discounted_amount) = PaymentReportService.get_total_amount_of_the_month(
                branch_id,year,month
            )

        branch:Branch = Branch.objects.select_related('branch_grade','country').get(id=branch_id)

        payment_serializer = self.get_serializer(queryset, many=True)
        loyalty_fees = PaymentReportService.get_royalty_fees(discounted_amount,branch)

        return Response({
            "success": True,
            "data": {
                "total_payments": len(payment_serializer.data),
                "payments": payment_serializer.data,
                "student_info":students,
                "branch_info": {
                    'branch_grade': branch.branch_grade.name,
                    'branch_percentage': branch.branch_grade.percentage,
                    'currency': branch.country.currency 
                },
                "attendances":attendances,
                "total_amount":self.format_decimal_points(total_amount),
                "total_discount":self.format_decimal_points(total_discount),
                "total_paid_amount":self.format_decimal_points(discounted_amount),
                "loyalty_fees":self.format_decimal_points(loyalty_fees)
            }
        })
    
class AllBranchPaymentReportListView(BaseCustomListNoPaginationAPIView,UtilsMixin):
    permission_classes = [IsSuperAdmin]
    serializer_class = BranchListReportSerializer

    def get_queryset(self,country):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        branches = Branch.objects.filter(country__name=country)

        return branches

    def list(self, request, *args, **kwargs):
        month = self.request.query_params.get('month')
        self.require_query_param(month,'month')
        year = self.request.query_params.get('year')
        self.require_query_param(year,'year')
        country = self.request.query_params.get('country')
        self.require_query_param(country,'country')
        
        branches = self.get_queryset(country)

        response_data = []

        sum_total_amount = 0
        sum_total_discount = 0
        sum_discounted_amount = 0
        sum_loyalty_fees = 0

        for branch in branches:
            (total_amount,total_discount,discounted_amount) = PaymentReportService.get_total_amount_of_the_month(
                branch.id,year,month
            )
  
            serializer = self.get_serializer(branch)
            branch_data = serializer.data

            total_amount = total_amount or 0
            total_discount = total_discount or 0
            discounted_amount = discounted_amount or 0

            loyalty_fees = PaymentReportService.get_royalty_fees(discounted_amount,branch)

            # Accumulate sums
            sum_total_amount += total_amount
            sum_total_discount += total_discount
            sum_discounted_amount += discounted_amount
            sum_loyalty_fees += loyalty_fees

            
            # Add payment data to the branch data
            branch_data['total_amount'] = self.format_decimal_points(total_amount or 0)
            branch_data['total_discount'] = self.format_decimal_points(total_discount or 0)
            branch_data['discounted_amount'] = self.format_decimal_points(discounted_amount or 0)
            branch_data['percentage'] = branch.branch_grade.percentage
            branch_data['loyalty_fees'] = self.format_decimal_points(loyalty_fees or 0)
            
            response_data.append(branch_data)

        attendances = PaymentReportService.get_attendance_statuses(year,month,country=country)

        currency = Country.objects.get(name=country).currency

        return Response({
            "success": True,
            "data": {
                "attendances":attendances,
                "payments": response_data,
                "total_amount": self.format_decimal_points(sum_total_amount),
                "total_discount": self.format_decimal_points(sum_total_discount),
                "discounted_amount": self.format_decimal_points(sum_discounted_amount),
                "currency": currency,
                "loyalty_fees":self.format_decimal_points(sum_loyalty_fees)
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
    
class MakePaymentView(BasePaymentView,UpdateAPIView):
    permission_classes = [IsManagerOrHigher]
    serializer_class = MakePaymentSerializer

    @transaction.atomic
    def update(self, request:Request, *args, **kwargs):
        try:
        
            instance = self.get_object()

            if instance.status == 'PAID' and instance.invoice:
                return Response({
                    "success": False,
                    "msg": "Invoice already paid."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self.perform_update(serializer)
            return Response({
                "success": True,
                "msg": "Payment made successfully."
            }, status=status.HTTP_204_NO_CONTENT)
    
        except ValidationError as e:
            # Handle both list and dictionary error messages
            if isinstance(e.detail, list):
                error_message = e.detail[0]  # Extract the first error message
            elif isinstance(e.detail, dict):
                first_error = next(iter(e.detail.values()))  # Get the first field's errors
                error_message = first_error[0] if isinstance(first_error, list) else str(first_error)
            else:
                error_message = str(e.detail)

            return Response({
                "success": False,
                "msg": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "success": False,
                "msg": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)