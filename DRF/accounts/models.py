from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class MyAccountManager(BaseUserManager):

    def create_user(self,username,email,password=None):
        if not email:
            raise ValueError("Kindly fill in the email")
        
        if not username:
            raise ValueError("Kindly fill in the username")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self,username,email, password):

        user = self.create_user(
            username,
            email=self.normalize_email(email),
            password=password
        )

        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        return user

class Role(models.Model):
    name            = models.CharField(max_length=20, unique=True)
    display_name    = models.CharField(max_length=20,null=True,blank=True)
    desciption      = models.CharField(max_length=20,null=True,blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
    
    def __str__(self):
        return self.name.capitalize()
    
    def save(self,*args, **kwargs) -> None:
        if not self.desciption:
            self.desciption = self.name.capitalize()
        if not self.display_name:
            self.display_name = self.name.capitalize()

        super(Role,self).save(*args,**kwargs)

    
'''
    -- User --
    first_name
    last_name
    username
    email
    email_verified_at
    password
    create_at
    updated_at
    is_first_login (is_password_changed)

    -- Profile --
    gender
    dob
    ic_number
    
    -- Ignore --
    remember_token
    delete_at
    terminated_at
    is_parent
    is_deshop_user
    deshop_id
'''    
# Create your models here.
class User(AbstractBaseUser):

    first_name          = models.CharField(max_length=50,null=True,blank=True)
    last_name           = models.CharField(max_length=50,null=True,blank=True)
    username            = models.CharField(max_length=50,unique=True)
    email               = models.EmailField(max_length=100,unique=True)
    email_verified_at   = models.DateTimeField(null=True,blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    last_login          = models.DateTimeField(auto_now_add=True)

    is_active           = models.BooleanField(default=True)
    is_staff            = models.BooleanField(default=True)
    is_superadmin       = models.BooleanField(default=False)
    is_password_changed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS=[
        'username'
    ]

    objects = MyAccountManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.username.capitalize()
    
    def has_perm(self,permission,obj=None)->bool:
        return self.is_superadmin
    
    def has_module_perms(self,add_label)->bool:
        return True
    
    def get_all_permissions(user=None):
        if user.is_superadmin:
            return set()
        
    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()
    
    def has_superadmin_role(self)->bool:
        return self.roles.filter(name='superadmin').exists()
    
class UserProfile(models.Model):
    GENDER = [('male','Male'),('female','Female')]
    
    user                = models.OneToOneField(User,on_delete=models.CASCADE,related_name='user_profile')
    gender              = models.CharField(choices=GENDER,max_length=6)
    dob                 = models.DateField(null=True,blank=True)
    ic_number           = models.CharField(max_length=100,null=True,blank=True)
    occupation          = models.CharField(max_length=100,null=True,blank=True)
    spouse_name         = models.CharField(max_length=100,null=True,blank=True) 
    spouse_phone        = models.CharField(max_length=100,null=True,blank=True) 
    spouse_occupation   = models.CharField(max_length=100,null=True,blank=True) 
    no_of_children      = models.IntegerField(null=True,blank=True) 
    personal_email      = models.EmailField(null=True,blank=True) 
    bank_name           = models.CharField(max_length=100,null=True,blank=True) 
    bank_account_name   = models.CharField(max_length=100,null=True,blank=True) 
    bank_account_number = models.CharField(max_length=100,null=True,blank=True) 
    
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        
    def __str__(self):
        return f"{self.user}'s profile" 
    