from django.db import models
from branches.models import Branch
from feeStructure.models import Grade
from students.models import Students

# Create your models here.
class StudentCertificate(models.Model):
    grade               = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    student             = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='certificates')
    branch              = models.ForeignKey(Branch, on_delete=models.PROTECT,related_name='certificates')
    start_date          = models.DateField()
    end_date            = models.DateField()
    status              = models.CharField(max_length=100)
    file_path           = models.URLField(null=True,blank=True)
    is_printed          = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'certificates'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-created_at']

    def __str__(self):
        return 'Certificate ' + self.id + ' - ' + self.student.fullname + 'Grade ' + str(self.grade.grade_level)