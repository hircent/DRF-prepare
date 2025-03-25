from django.contrib import admin
from .models import InvoiceSequence,Invoice,Payment,PromoCode

# Register your models here.
class InvoiceSequenceAdmin(admin.ModelAdmin):
    list_display = ('id','branch','number','year')
    list_filter = ('branch',)
    search_fields = ('branch__name',)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id','branch','invoice_sequence','paid_at')
    list_filter = ('branch',)
    raw_id_fields = ('invoice_sequence','branch')

    search_fields = ('branch__name',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','enrolment','enrolment_id','invoice','amount','paid_amount','status','enrolment_type')
    list_filter = ('status',)
    raw_id_fields = ('enrolment','invoice')

    search_fields = ('enrolment__student__fullname',)
    readonly_fields = ('id','created_at','updated_at')

class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('id','code','amount','min_purchase_amount','quantity','used','expired_at')
    list_filter = ('branch','for_all_branches','promo_type')
    search_fields = ('code',)


admin.site.register(InvoiceSequence,InvoiceSequenceAdmin)
admin.site.register(Invoice,InvoiceAdmin)    
admin.site.register(Payment,PaymentAdmin)
admin.site.register(PromoCode,PromoCodeAdmin)