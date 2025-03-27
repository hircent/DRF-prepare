from branches.models import Branch
from rest_framework import serializers
from .models import Invoice,Payment,PromoCode
from .service import PaymentService

class StudentPaymentListSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id','status','amount','discount','paid_amount','pre_outstanding','post_outstanding','start_date','grade','enrolment_type']
        
    def get_grade(self, obj):
        return obj.enrolment.grade.grade_level

class PaymentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id','status']

class PaymentReportListSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    paid_at = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id','student','grade','enrolment_type','paid_at','amount','status']

    def get_student(self, obj):
        return obj.enrolment.student.fullname

    def get_grade(self, obj):
        return obj.enrolment.grade.grade_level
    
    def get_paid_at(self, obj):
        if not obj.invoice:
            return None
        return obj.invoice.paid_at.strftime("%Y-%m-%d")
    
    def get_amount(self, obj:Payment):
        return "{:.2f}".format(float(obj.amount - obj.discount))

class PaymentDetailsSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id','status','amount','discount','paid_amount','pre_outstanding','post_outstanding','start_date','grade','student','currency']
        
    def get_grade(self, obj:Payment):
        return obj.enrolment.grade.grade_level
    
    def get_student(self, obj:Payment):
        return obj.enrolment.student.fullname
    
    def get_currency(self,obj:Payment):
        return obj.enrolment.branch.country.currency

class InvoiceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        exclude = ('created_at', 'updated_at')

class PromoCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCode
        exclude = ('created_at', 'updated_at')

class PromoCodeCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCode
        exclude = ('created_at', 'updated_at')

    def validate(self, data):
        for_all_branches = data.get("for_all_branches")
        branch = data.get("branch", None)
        
        if for_all_branches and branch:
            raise serializers.ValidationError("Branch must be null when 'for_all_branches' is True.")
        
        if not for_all_branches and not branch:
            raise serializers.ValidationError("Branch is required when 'for_all_branches' is False.")

        return data
    
    def create(self, validated_data):
        return PromoCode.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
class MakePaymentSerializer(serializers.ModelSerializer):
    promo_code = serializers.PrimaryKeyRelatedField(
        queryset=PromoCode.objects.all(),
        error_messages={
            'does_not_exist': 'Invalid Promo Code.',
        }
    )

    class Meta:
        model = Payment
        fields = ['promo_code','paid_amount']

    def validate_promo_code(self, value):
        if value:
            branchId = self.context.get('request').headers.get('branchId')
            pm = PromoCode.objects.get(id=value.id)

            if not pm.for_all_branches:
                if not pm.branch:
                    raise serializers.ValidationError("Promo code is not configured for any branch")
                
                # Branch must match the request branch
                if pm.branch.id != branchId:
                    raise serializers.ValidationError("Promo code is not valid for this branch")
            
        return value

    def update(self, instance:Payment, validated_data):
        promo_discount = validated_data.get('promo_code',None)
        paid_amount = validated_data.get('paid_amount')
        discounted_amount = instance.amount

        if promo_discount:
            discounted_amount = instance.amount - promo_discount.amount
        
        amount_to_pay = self._get_amount_to_pay(instance,discounted_amount) 

        if not self._validate_amount_to_pay(paid_amount,amount_to_pay):
            raise serializers.ValidationError(f"Amount to pay: {amount_to_pay}")
        
        after_payment_remaining = self._after_payment(paid_amount,amount_to_pay)
        
        instance.post_outstanding += after_payment_remaining
        instance.discount = promo_discount.amount if promo_discount else 0
        instance.paid_amount = paid_amount
        instance.promo_code = promo_discount
        invoice = PaymentService.create_invoice(instance.enrolment.branch)
        instance.invoice = invoice
        instance.save()

        return instance
    
    def _get_amount_to_pay(self,payment:Payment,discount_amount:float):
        if payment.pre_outstanding >= discount_amount:
            payment.pre_outstanding -= discount_amount
            return 0
        else:
            return discount_amount - payment.pre_outstanding
        
    def _validate_amount_to_pay(self,paid_amount:float,amount_to_pay:float):

        if paid_amount >= amount_to_pay:
            return True
        return False
    
    def _after_payment(self,paid_amount:float,amount_to_pay:float):
        return paid_amount - amount_to_pay

    
