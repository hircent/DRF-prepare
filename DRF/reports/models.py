from django.db import models
from branches.models import Branch
from students.models import Students
from payments.models import Payment

# Create your models here.
class PaymentReport(models.Model):
    branch              = models.ForeignKey(Branch, on_delete=models.PROTECT,related_name='payment_reports')
    # payment             = models.ForeignKey(Payment, on_delete=models.PROTECT,null=True,blank=True,related_name='payment_reports')
    action              = models.CharField(max_length=100)
    action_datetime     = models.DateTimeField()
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_reports'
        verbose_name = 'Payment Report'
        verbose_name_plural = 'Payment Reports'
        ordering = ['-action_datetime']

    def __str__(self):        
        return 'Payment Report ' + self.id + ' - ' + self.student.fullname