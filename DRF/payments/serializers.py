from branches.models import Branch
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
    