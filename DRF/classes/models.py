from django.db import models
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import User
from branches.models import Branch
from students.models import Students
# Create your models here.
class Class(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    branch              = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name                = models.CharField(max_length=255)
    label               = models.CharField(max_length=255)
    description         = models.TextField()
    commencement_date   = models.DateField()
    time                = models.TimeField()
    days                = models.CharField(max_length=255, choices=DAY_CHOICES)
    students            = models.ManyToManyField('Students', through='StudentEnrolment')
    total_enrolled      = models.IntegerField(
                                default=0,
                                validators=[MaxValueValidator(6, "Maximum 6 students can be enrolled")]
                            )
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'classes'
        ordering = ['-start_date']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        
    def __str__(self):
        return self.name
    
    def clean(self):
        # Additional validation to ensure total_enrolled matches actual enrollment
        if self.id and self.students.count() > 6:
            raise ValidationError("This class cannot have more than 6 students")

class StudentEnrolment(models.Model):
    student             = models.ForeignKey(Students, on_delete=models.CASCADE)
    class_instance      = models.ForeignKey(Class, on_delete=models.CASCADE)
    branch              = models.ForeignKey(Branch, on_delete=models.CASCADE)
    enrollment_date     = models.DateTimeField(auto_now_add=True)
    is_active           = models.BooleanField(default=True)
    remaining_lessons   = models.IntegerField(default=24)

    class Meta:
        unique_together = ['student', 'class_instance']
        verbose_name = 'Class Enrollment'
        verbose_name_plural = 'Class Enrollments'

    def save(self, *args, **kwargs):
        if self.remaining_lessons <= 0:
            self.is_active = False
        super().save(*args, **kwargs)

class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('ATTENDED', 'Attended'),
        ('ABSENT', 'Absent'),
        ('FREEZED', 'Freezed'),
    ]
    
    enrollment  = models.ForeignKey(StudentEnrolment, on_delete=models.CASCADE)
    branch      = models.ForeignKey(Branch, on_delete=models.CASCADE)
    teacher     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date        = models.DateField()
    status      = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES)
    notes       = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['enrollment', 'date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'

    def save(self, *args, **kwargs):
        # Check if this is a new attendance record
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            # Get the old status before saving
            old_status = Attendance.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if is_new:
            # New attendance record
            if self.status in ['PRESENT', 'ABSENT']:
                self.enrollment.remaining_lessons -= 1
            elif self.status == 'EXCUSED':
                self.enrollment.remaining_lessons += 1
        else:
            # Status change on existing record
            if old_status != self.status:
                if old_status in ['PRESENT', 'ABSENT'] and self.status == 'EXCUSED':
                    # Changed from PRESENT/ABSENT to EXCUSED, add back two lessons
                    self.enrollment.remaining_lessons += 2
                elif old_status == 'EXCUSED' and self.status in ['PRESENT', 'ABSENT']:
                    # Changed from EXCUSED to PRESENT/ABSENT, remove two lessons
                    self.enrollment.remaining_lessons -= 2

        self.enrollment.save()