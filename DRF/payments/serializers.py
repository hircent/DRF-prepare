from rest_framework import serializers

from .models import InvoiceSequence,Invoice,Payment

class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        
        write_only_fields = ('created_at','updated_at')