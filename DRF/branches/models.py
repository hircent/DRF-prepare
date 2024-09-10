from django.db import models
# from accounts.models import User
# Create your models here.

class BranchGrade(models.Model):
    name = models.CharField(max_length=20)
    percentage = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "branch_grades"
        verbose_name = "Branch_Grade"
        verbose_name_plural = "Branch_Grades"

    def __str__(self):
        return self.name
    
class Branch(models.Model):
    branch_grade = models.ForeignKey(BranchGrade, on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=100,unique=True)
    display_name = models.CharField(max_length=100,null=True,blank=True)
    business_name = models.CharField(max_length=100,null=True,blank=True)
    business_reg_no = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    '''
    principal = Principal.objects.get(id=1)
    academies = principal.academies.all()  # Access all academies related to the principal
    '''
    # principal = models.ForeignKey(User,blank=True,null=True,on_delete=models.SET_NULL,related_name="academies")
    operation_date = models.DateField(null=False,blank=False)
    is_headquaters = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    terminated_at = models.DateTimeField(blank=True,null=True)

    class Meta:
        db_table = "branches"
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def save(self,*args,**kwargs):
        if not self.business_name:
            self.business_name = self.name.upper()
        if not self.display_name:
            self.display_name = self.name.upper()
        
        super(Branch,self).save(*args,**kwargs)

    def __str__(self):
        return self.name
    

