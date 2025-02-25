from django.contrib import admin
from .models import InvoiceSequence,Invoice,Payment
# Register your models here.
class InvoiceSequenceAdmin(admin.ModelAdmin):
    list_display = ('branch','number')

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('branch','invoice_sequence','created_at')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrolment','invoice','amount','paid_amount','status','description')

admin.site.register(InvoiceSequence,InvoiceSequenceAdmin)
admin.site.register(Invoice,InvoiceAdmin)    
admin.site.register(Payment,PaymentAdmin)