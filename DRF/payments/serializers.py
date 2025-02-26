from accounts.serializers import ParentDetailSerializer
from rest_framework import serializers
from .models import Invoice,Payment

class PaymentListSerializer(serializers.ModelSerializer):
    parent = ParentDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        exclude = ('created_at', 'updated_at')

class InvoiceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        exclude = ('created_at', 'updated_at')