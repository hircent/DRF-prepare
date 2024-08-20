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
            last_name = last_name
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

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        return user

        
    
# Create your models here.
class SuperAdmin(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=50)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS=[
        'username','first_name','last_name'
    ]

    objects = MyAccountManager()

    class Meta:
        db_table = 'superadmins'
        verbose_name = 'Super Admin'
        verbose_name_plural = 'Super Admins'

    def __str__(self) -> str:
        return self.email
    
    def has_perm(self,permission,obj=None)->bool:
        return self.is_admin
    
    def has_module_perms(self,add_label)->bool:
        return True
    
    def get_all_permissions(user=None):
        if user.is_superadmin:
            return set()