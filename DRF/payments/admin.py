from django.contrib import admin
from .models import InvoiceSequence,Invoice,Payment
# Register your models here.
class InvoiceSequenceAdmin(admin.ModelAdmin):
    list_display = ('id','branch','number','year')

    search_fields = ('branch__name',)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id','branch','invoice_sequence','created_at')

    raw_id_fields = ('invoice_sequence','branch')

    search_fields = ('branch__name',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','enrolment','enrolment_id','invoice','amount','paid_amount','status','description')

    raw_id_fields = ('enrolment','invoice')

    search_fields = ('enrolment__student__fullname',)

    list_filter = ('status',)

admin.site.register(InvoiceSequence,InvoiceSequenceAdmin)
admin.site.register(Invoice,InvoiceAdmin)    
admin.site.register(Payment,PaymentAdmin)