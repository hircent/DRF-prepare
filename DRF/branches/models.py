from django.db import models
from accounts.models import User
# Create your models here.
class Branch(models.Model):
    name = models.CharField(max_length=100,unique=True)
    '''
    principal = Principal.objects.get(id=1)
    academies = principal.academies.all()  # Access all academies related to the principal
    '''
    principal = models.ForeignKey(User,blank=True,null=True,on_delete=models.SET_NULL,related_name="academies")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "branches"
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name