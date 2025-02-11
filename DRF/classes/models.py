from django.db import models

from accounts.models import User
from branches.models import Branch
from category.models import Category,Grade
from students.models import Students
from category.models import Theme,ThemeLesson
from django.utils import timezone
from datetime import timedelta

class Class(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    CATEGORY_CHOICES = [
        ('Kiddo', 'Kiddo'),
        ('Kids', 'Kids'),
        ('Superkids', 'Superkids'),
    ]
    
    branch              = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name                = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    label               = models.CharField(max_length=100)
    start_date          = models.DateField()
    start_time          = models.TimeField()
    end_time            = models.TimeField()
    day                 = models.CharField(max_length=50, choices=DAY_CHOICES)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'classes'
        ordering = ['-start_time']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        
    def __str__(self):
        return self.name

class StudentEnrolment(models.Model):
    ENROLMENT_STATUS_CHOICES = [
        ('IN_PROGRESS', 'IN PROGRESS'),
        ('COMPLETED', 'COMPLETED'),
        ('DROPPED_OUT', 'DROPPED OUT'),
    ]
    branch              = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='enrolments')
    grade               = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    student             = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='enrolments')
    classroom           = models.ForeignKey(Class, on_delete=models.CASCADE,related_name='enrolments')
    start_date          = models.DateField()
    is_active           = models.BooleanField(default=True)
    status              = models.CharField(max_length=20, choices=ENROLMENT_STATUS_CHOICES,default='IN_PROGRESS')
    remaining_lessons   = models.IntegerField(default=24)
    freeze_lessons      = models.IntegerField(default=4)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_enrolments'
        verbose_name = 'Student Enrollment'
        verbose_name_plural = 'Student Enrollments'

    def __str__(self):
        return self.student.fullname + "'s enrolment " + str(self.start_date.year)

    def save(self, *args, **kwargs):
        if self.remaining_lessons <= 0:
            self.is_active = False
        super().save(*args, **kwargs)

class ClassLesson(models.Model):
    LESSON_STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED')
    ]

    branch              = models.ForeignKey(Branch,on_delete=models.CASCADE,related_name='class_lessons')
    class_instance      = models.ForeignKey(Class, on_delete=models.CASCADE,related_name='lessons')
    teacher             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name='teacher_class_lessons')
    co_teacher          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name='co_teacher_class_lessons')
    theme_lesson        = models.ForeignKey(ThemeLesson,on_delete=models.SET_NULL, null=True, blank=True,related_name='class_theme_lessons')
    date                = models.DateField()
    start_datetime      = models.DateTimeField(null=True)
    end_datetime        = models.DateTimeField(null=True)
    status              = models.CharField(max_length=10, choices=LESSON_STATUS_CHOICES,default='PENDING')
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'class_lessons'
        ordering = ['-date']
        verbose_name = 'Class Lesson'
        verbose_name_plural = 'Class Lessons'

    def __str__(self):
        return str(self.id) + ' '+ self.class_instance.name + ' ' + self.class_instance.day + " - " + str(self.class_instance.start_time)

class StudentAttendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('ATTENDED', 'ATTENDED'),
        ('ABSENT', 'ABSENT'),
        ('FREEZED', 'FREEZED'),
        ('SFREEZED', 'SFREEZED'),
        ('REPLACEMENT', 'REPLACEMENT'),
    ]

    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    enrollment      = models.ForeignKey(StudentEnrolment, on_delete=models.CASCADE,related_name='attendances')
    branch          = models.ForeignKey(Branch, on_delete=models.SET_NULL,null=True)
    class_lesson    = models.ForeignKey(ClassLesson, on_delete=models.CASCADE,related_name='attendances')
    date            = models.DateField()
    day             = models.CharField(max_length=50, choices=DAY_CHOICES)
    start_time      = models.TimeField()
    end_time        = models.TimeField()
    has_attended    = models.BooleanField(default=False)
    status          = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_attendances'
        # unique_together = ['enrollment', 'class_lesson' ,'date']
        verbose_name = 'Student Attendance'
        verbose_name_plural = 'Student Attendances'

    def __str__(self) -> str:
        return self.enrollment.student.fullname + "'s attendance"
    
    def save(self, *args, **kwargs):
        if not self.day:
            self.day = self.date.strftime("%A")
        super().save(*args, **kwargs)


class EnrolmentExtension(models.Model):
    enrolment   = models.ForeignKey(StudentEnrolment, on_delete=models.CASCADE,related_name='extensions')
    branch      = models.ForeignKey(Branch, on_delete=models.SET_NULL,null=True,related_name='enrolment_extensions')
    start_date  = models.DateField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrolment_extensions'
        verbose_name = 'Enrolment Extension'
        verbose_name_plural = 'Enrolment Extensions'

    def __str__(self) -> str:
        return self.enrolment.student.fullname + "'s enrolment extension"
    

class VideoAssignment(models.Model):
    enrolment       = models.ForeignKey(StudentEnrolment, on_delete=models.CASCADE,related_name='video_assignments')
    theme           = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)
    video_url       = models.URLField(null=True,blank=True)
    video_number    = models.PositiveIntegerField(blank=True)
    submission_date = models.DateField(null=True,blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'video_assignments'
        verbose_name = 'Video Assignment'
        verbose_name_plural = 'Video Assignments'
        ordering = ['video_number']

    def __str__(self) -> str:
        return self.enrolment.student.fullname + "'s video assignment " + str(self.video_number)

class ReplacementAttendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('ATTENDED', 'ATTENDED'),
        ('ABSENT', 'ABSENT'),
        ('PENDING', 'PENDING'),
    ]

    attendances         = models.OneToOneField(StudentAttendance, on_delete=models.CASCADE,related_name='replacement_attendances')
    class_instance      = models.ForeignKey(Class, on_delete=models.CASCADE,related_name='replacement_attendances')
    date                = models.DateField()
    status              = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES,default='PENDING')
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'replacement_attendances'
        verbose_name = 'Replacement Attendance'
        verbose_name_plural = 'Replacement Attendances'
        indexes = [
            models.Index(fields=['attendances', 'class_instance', 'date']),
        ]

    def __str__(self) -> str:
        return self.attendances.enrollment.student.fullname + "'s replacement attendance at " + str(self.date)