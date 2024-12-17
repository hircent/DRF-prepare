from accounts.models import User
from branches.models import Branch ,UserBranchRole
from django.db import models

'''
    - Student
    branch
    parent
    first_name
    last_name
    gender
    dob
    school
    deemcee_starting_grade
    enrolment_date
    
    referral_channel_id
    referral
    
    starter_kits
    remark
    
    created_at
    updated_at
    status

    - StudentEnrolments
    grade_id
    commencement_date
    end_date
    voucher
    last_payment_date
    status
    status = [('in_progress','IN_PROGRESS'),('dropped_out','DROPPED_OUT'),('graduated','GRADUATED'),('extended','EXTENDED')]
'''
# Create your models here.
class Students(models.Model):
    GENDER = [
        ('Male','Male'),
        ('Female','Female')
    ]
    STATUS = [
        ('IN_PROGRESS','IN_PROGRESS'),
        ('DROPPED_OUT','DROPPED_OUT'),
        ('GRADUATED','GRADUATED')
    ]

    branch                  = models.ForeignKey(Branch,on_delete=models.CASCADE,related_name='students')
    parent                  = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='children')
    first_name              = models.CharField(max_length=50,null=True,blank=True)
    last_name               = models.CharField(max_length=50,null=True,blank=True)
    fullname                = models.CharField(max_length=50)
    gender                  = models.CharField(choices=GENDER,max_length=6)
    dob                     = models.DateField(null=True,blank=True)
    school                  = models.CharField(max_length=100)
    deemcee_starting_grade  = models.IntegerField(null=True,blank=True)
    # referral_channel_id     = models.IntegerField()
    # referral                = models.IntegerField()
    status                  = models.CharField(choices=STATUS,max_length=12,default='IN_PROGRESS')

    enrolment_date          = models.DateField()
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        managed = True #True by default, false if have legacy table in db , django wont create table during migrations
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return self.fullname
    