from branches.models import Branch
from rest_framework import serializers
from .models import Invoice,Payment,PromoCode

class StudentPaymentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        exclude = ('created_at', 'updated_at','enrolment')

class PaymentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id','status']

class PaymentDetailsSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id','status','amount','discount','paid_amount','pre_outstanding','post_outstanding','start_date','grade','student']
        
    def get_grade(self, obj):
        return obj.enrolment.grade.grade_level
    
    def get_student(self, obj):
        return obj.enrolment.student.fullname

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
    