from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class MyAccountManager(BaseUserManager):

    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError("Kindly fill in the email")
        
        if not username:
            raise ValueError("Kindly fill in the username")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, first_name,last_name,username,email, password):

        user = self.create_user(
            first_name,
            last_name,
            username,
            email=self.normalize_email(email),
            password=password
        )

        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        return user

class Role(models.Model):
    name = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=20,null=True,blank=True)
    desciption = models.CharField(max_length=20,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

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

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    email_verified_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    is_password_changed = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS=[
        'first_name','last_name','email'
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
    
