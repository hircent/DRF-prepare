from django.contrib import admin
from .models import PaymentReport
# Register your models here.

class PaymentReportAdmin(admin.ModelAdmin):
    list_display = ('branch','payment','action','action_datetime')

admin.site.register(PaymentReport,PaymentReportAdmin)
