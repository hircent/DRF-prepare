from rest_framework import serializers
from .models import Invoice,Payment,PromoCode

class PaymentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id','status']

class InvoiceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        exclude = ('created_at', 'updated_at')

class PromoCodeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCode
        exclude = ('created_at', 'updated_at')