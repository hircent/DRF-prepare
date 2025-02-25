from django.contrib import admin
from .models import InvoiceSequence,Invoice,Payment
# Register your models here.
class InvoiceSequenceAdmin(admin.ModelAdmin):
    list_display = ('id','branch','number','year')

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id','branch','invoice_sequence','created_at')

    raw_id_fields = ('invoice_sequence','branch')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','enrolment','invoice','amount','paid_amount','status','description')

    raw_id_fields = ('enrolment','invoice')

admin.site.register(InvoiceSequence,InvoiceSequenceAdmin)
admin.site.register(Invoice,InvoiceAdmin)    
admin.site.register(Payment,PaymentAdmin)