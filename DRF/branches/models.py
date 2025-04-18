from accounts.models import User ,Role
from country.models import Country
from django.db import models
# Create your models here.

class BranchGrade(models.Model):
    name        = models.CharField(max_length=20)
    percentage  = models.IntegerField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "branch_grades"
        verbose_name = "Branch Grade"
        verbose_name_plural = "Branch Grades"

    def __str__(self):
        return self.name
    
class Branch(models.Model):
    branch_grade    = models.ForeignKey(BranchGrade, on_delete=models.SET_NULL,null=True,default=1)
    country         = models.ForeignKey(Country, on_delete=models.PROTECT,default=1)
    name            = models.CharField(max_length=100,unique=True)
    display_name    = models.CharField(max_length=100,null=True,blank=True)
    business_name   = models.CharField(max_length=100,null=True,blank=True)
    business_reg_no = models.CharField(max_length=100,null=True,blank=True)
    description     = models.TextField(null=True,blank=True)
    '''
    principal = Principal.objects.get(id=1)
    academies = principal.academies.all()  # Access all academies related to the principal
    '''
    # principal = models.ForeignKey(User,blank=True,null=True,on_delete=models.SET_NULL,related_name="academies")
    operation_date  = models.DateField(null=False,blank=False)
    is_headquaters  = models.BooleanField(default=False)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now_add=True)
    terminated_at   = models.DateTimeField(blank=True,null=True)

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
        return self.name.capitalize()
    
class BranchAddress(models.Model):
    branch = models.OneToOneField(Branch,on_delete=models.CASCADE,related_name='branch_address')
    address_line_1 = models.CharField(max_length=120,null=True,blank=True)
    address_line_2 = models.CharField(max_length=120,null=True,blank=True)
    address_line_3 = models.CharField(max_length=120,null=True,blank=True)
    postcode = models.CharField(max_length=10,null=True,blank=True)
    city = models.CharField(max_length=50,null=True,blank=True)
    state = models.CharField(max_length=50,null=True,blank=True)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.branch.name.capitalize()
    
    class Meta:
        db_table = "branch_addresses"
        verbose_name = "Branch Address"
        verbose_name_plural = "Branch Addresses"

class UserBranchRole(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE,related_name='users')
    branch      = models.ForeignKey(Branch, on_delete=models.CASCADE,related_name='user_branch')
    role        = models.ForeignKey(Role, on_delete=models.CASCADE,related_name='user_roles')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_branch_roles"
        verbose_name = "User Branch Role"
        verbose_name_plural = "User Branch Roles"
        unique_together = ('branch', 'role', 'user')

    def __str__(self):
        return f'{self.user.email} is {self.role.name} at {self.branch.name}'