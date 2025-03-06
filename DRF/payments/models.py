from django.db import models
from accounts.models import User
from branches.models import Branch
from classes.models import StudentEnrolment
from datetime import datetime

# Create your models here.

class PromoCode(models.Model):
    PROMO_TYPE_CHOICES = [
        ('ENROLMENT','ENROLMENT'),
        ('MERCHANDISE','MERCHANDISE'),
        ('OTHER','OTHER')
    ]
    code             = models.CharField(max_length=100,unique=True)
    amount           = models.DecimalField(max_digits=10, decimal_places=2)
    quantity         = models.PositiveIntegerField()
    used             = models.PositiveIntegerField(default=0)
    branch           = models.ForeignKey(Branch,on_delete=models.SET_NULL,null=True,blank=True,related_name='promo_codes')
    for_all_branches = models.BooleanField(default=False)
    promo_type       = models.CharField(max_length=100,choices=PROMO_TYPE_CHOICES)
    expired_at       = models.DateField()
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'promo_codes'
        verbose_name = 'Promo Code'
        verbose_name_plural = 'Promo Codes'

    def __str__(self):
        return self.code

class InvoiceSequence(models.Model):
    branch      = models.ForeignKey(Branch, on_delete=models.PROTECT,related_name='sequences')
    number      = models.PositiveIntegerField(default=1)
    year        = models.PositiveIntegerField(default=datetime.now().year)

    class Meta:
        db_table = 'invoice_sequences'
        verbose_name = 'Invoice Sequence'
        verbose_name_plural = 'Invoice Sequences'
        ordering = ['-number']

    def __str__(self):
        return  f"MY{self.branch.id:03d} - {self._get_year_last_two_digits} - {self.number:04d}"

    @property
    def _get_year_last_two_digits(self):
        return int(str(self.year)[2:])

class Invoice(models.Model):
    branch              = models.ForeignKey(Branch, on_delete=models.PROTECT,related_name='invoices')
    invoice_sequence    = models.OneToOneField(InvoiceSequence, on_delete=models.PROTECT,related_name='sequence')
    file_path           = models.URLField(null=True,blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Invoice {self.id} - {self.invoice_sequence.number:04d}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'PAID'),
        ('PARTIALLY_PAID', 'PARTIALLY_PAID'),
        ('UNPAID', 'UNPAID'),
        ('REFUNDED', 'REFUNDED'),
        ('VOIDED', 'VOIDED'),
    ]

    enrolment           = models.ForeignKey(StudentEnrolment, on_delete=models.PROTECT,related_name='payments')
    invoice             = models.OneToOneField(Invoice, on_delete=models.PROTECT,related_name='payment')
    parent              = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    amount              = models.DecimalField(max_digits=10, decimal_places=2)
    discount            = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    paid_amount         = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    start_date          = models.DateField()
    status              = models.CharField(max_length=100,default='UNPAID',choices=STATUS_CHOICES)
    description         = models.CharField(max_length=100,null=True,blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return 'Payment ' + str(self.id) + ' - ' + self.enrolment.student.fullname
    
    def save(self, *args, **kwargs):
        if self.paid_amount is None or self.paid_amount == 0:
            self.status = 'UNPAID'
        elif self.paid_amount >= self.amount:
            self.status = 'PAID'
        else:
            self.status = 'PARTIALLY_PAID'

        if not self.parent and self.enrolment:
            self.parent = self.enrolment.student.parent
        
        super().save(*args, **kwargs)