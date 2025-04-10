from branches.serializers import BranchDetailsSerializer
from rest_framework import serializers
from .models import Invoice,Payment,PromoCode
from .service import PaymentService
from accounts.models import User

class StudentPaymentListSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()
    enrolment_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id','status','amount','discount','early_advance_rebate','paid_amount','pre_outstanding','post_outstanding','start_date','grade','enrolment_type']
        
    def get_grade(self, obj):
        return obj.enrolment.grade.grade_level
    
    def get_enrolment_type(self, obj):
        return obj.get_enrolment_type_display() if obj.enrolment_type else None

class PaymentListSerializer(serializers.ModelSerializer):
    paid_at = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id','status','amount','paid_at']

    def get_paid_at(self, obj):
        if not obj.invoice:
            return None
        return obj.invoice.paid_at.strftime("%Y-%m-%d")

class PaymentReportListSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    paid_at = serializers.SerializerMethodField()
    discounted_amount = serializers.SerializerMethodField()
    class Meta:
        model = Payment
        fields = ['id','student','grade','enrolment_type','paid_at','amount','discount','early_advance_rebate','discounted_amount','start_date']

    def get_student(self, obj):
        return obj.enrolment.student.fullname

    def get_grade(self, obj):
        return obj.enrolment.grade.grade_level
    
    def get_paid_at(self, obj):
        if not obj.invoice:
            return None
        return obj.invoice.paid_at.strftime("%Y-%m-%d")
    
    def get_discounted_amount(self, obj:Payment):
        discounted_amount = obj.amount - obj.discount - obj.early_advance_rebate
        return "{:.2f}".format(float(discounted_amount))

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
    promo_code = serializers.IntegerField()

    class Meta:
        model = Payment
        fields = ['promo_code','paid_amount']

    def validate_promo_code(self, value):
        if value != 0:
            branchId = self.context.get('request').headers.get('branchId')

            promo_code = PromoCode.objects.filter(id=value)

            if not promo_code.exists():
                raise serializers.ValidationError("Promo code does not exist")
            pm = promo_code.first()

            if not pm.for_all_branches:
                if not pm.branch:
                    raise serializers.ValidationError("Promo code is not configured for any branch")
                
                # Branch must match the request branch
                if pm.branch.id != int(branchId):
                    raise serializers.ValidationError("Promo code is not valid for this branch")
            
        return value

    def update(self, instance:Payment, validated_data):
        promo_code = validated_data.get('promo_code')
        paid_amount = validated_data.get('paid_amount')
        discounted_amount = instance.amount

        promo_discount = 0
        if promo_code != 0:
            promo_code = PromoCode.objects.filter(id=promo_code)

            if not promo_code.exists():
                raise serializers.ValidationError("Promo code does not exist")

            promo_discount = promo_code.first().amount
            instance.promo_code = promo_code.first()

        discounted_amount = instance.amount - promo_discount 

        pre_outstanding = instance.pre_outstanding

        amount_to_pay = self._get_amount_to_pay(pre_outstanding,discounted_amount) 

        if not self._validate_amount_to_pay(paid_amount,amount_to_pay):
            raise serializers.ValidationError(f"Amount to pay: {amount_to_pay}")
        
        after_payment_remaining = self._after_payment(paid_amount,promo_discount,instance)
        
        instance.post_outstanding += after_payment_remaining
        instance.discount = promo_discount
        instance.paid_amount = paid_amount
        invoice = PaymentService.create_invoice(instance.enrolment.branch)
        instance.invoice = invoice
        instance.save()

        return instance
    
    def _get_amount_to_pay(self,pre_outstanding:float,discounted_amount:float):
        if pre_outstanding >= discounted_amount:
            return 0
        else:
            return discounted_amount - pre_outstanding
        
    def _validate_amount_to_pay(self,paid_amount:float,amount_to_pay:float):
        if paid_amount >= amount_to_pay:
            return True
        return False
    
    def _after_payment(self,paid_amount:float,discount_amount:float,payment:Payment):
        pre_outstanding = payment.pre_outstanding
        amount = payment.amount

        if pre_outstanding >= (amount - discount_amount):
            return pre_outstanding - (amount - discount_amount)
        else:
            return abs((amount - discount_amount) - paid_amount - pre_outstanding) 

    
class PaymentInvoiceDetailsForPrintSerializer(serializers.ModelSerializer):
    branch = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    invoice = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    enrolment_type = serializers.SerializerMethodField()
    amount_to_pay = serializers.SerializerMethodField()
    promo_code = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id','student','grade','invoice','parent','enrolment_type',
            'amount','amount_to_pay','discount','promo_code','early_advance_rebate',
            'paid_amount','pre_outstanding','post_outstanding',
            'start_date','status','branch'
        ]

    def get_promo_code(self, obj:Payment):
        return obj.promo_code.code if obj.promo_code else "Promo 1"

    def get_amount_to_pay(self,obj:Payment):
        amount_to_pay = obj.amount - obj.discount - obj.early_advance_rebate
        return f"{amount_to_pay:.2f}"

    def get_branch(self, obj:Payment):
        return BranchDetailsSerializer(obj.enrolment.branch).data
    
    def get_grade(self, obj:Payment):
        return obj.enrolment.grade.grade_level
    
    def get_invoice(self, obj:Payment):
        return obj.invoice.invoice_sequence.invoice_number
    
    def get_student(self, obj:Payment):
        return obj.enrolment.student.fullname.capitalize()
    
    def get_enrolment_type(self, obj:Payment):
        return obj.get_enrolment_type_display() if obj.enrolment_type else None
    
    def get_parent(self, obj:Payment):
        user:User = User.objects.prefetch_related('user_profile','user_address').get(id=obj.parent.id)
        return {
            "id": user.id,
            "first_name": user.first_name.capitalize() if user.first_name else "-",
            "last_name": user.last_name.capitalize() if user.last_name else "-",
            "username": user.username,
            "email": user.email,
            "details": {
                "gender": user.user_profile.gender,
                "dob": user.user_profile.dob,
                "ic_number": user.user_profile.ic_number,
                "occupation": user.user_profile.occupation,
                "phone": user.user_profile.phone,
                "spouse_name": user.user_profile.spouse_name,
                "spouse_phone": user.user_profile.spouse_phone,
                "spouse_occupation": user.user_profile.spouse_occupation,
                "no_of_children": user.user_profile.no_of_children,
                "personal_email": user.user_profile.personal_email,
                "bank_name": user.user_profile.bank_name,
                "bank_account_name": user.user_profile.bank_account_name,
                "bank_account_number": user.user_profile.bank_account_number
            },
            "address": {
                "address_line_1": user.user_address.address_line_1,
                "address_line_2": user.user_address.address_line_2,
                "address_line_3": user.user_address.address_line_3,
                "postcode": user.user_address.postcode,
                "city": user.user_address.city,
                "state": user.user_address.state
            }
        }