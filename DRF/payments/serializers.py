from rest_framework import serializers
from .models import Invoice,Payment

class PaymentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id','status']

class InvoiceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        exclude = ('created_at', 'updated_at')