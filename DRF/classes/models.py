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
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DROPPED_OUT', 'Dropped Out'),
    ]
    branch              = models.ForeignKey(Branch, on_delete=models.CASCADE)
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
        return self.student.fullname + "'s enrolment"

    def save(self, *args, **kwargs):
        if self.remaining_lessons <= 0:
            self.is_active = False
        super().save(*args, **kwargs)

class ClassLesson(models.Model):
    LESSON_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed')
    ]

    branch              = models.ForeignKey(Branch,on_delete=models.CASCADE,related_name='class_lessons')
    class_instance      = models.ForeignKey(Class, on_delete=models.CASCADE,related_name='lessons')
    teacher             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name='teacher_class_lessons')
    co_teacher          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name='co_teacher_class_lessons')
    theme_lesson        = models.ForeignKey(ThemeLesson,on_delete=models.SET_NULL, null=True,related_name='class_theme_lessons')
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
        return self.class_instance.name + "-" + self.date.strftime("%d-%m-%Y")

# class Attendance(models.Model):
#     ATTENDANCE_CHOICES = [
#         ('ATTENDED', 'Attended'),
#         ('ABSENT', 'Absent'),
#         ('FREEZED', 'Freezed'),
#     ]
    
#     enrollment  = models.ForeignKey(StudentEnrolment, on_delete=models.CASCADE)
#     branch      = models.ForeignKey(Branch, on_delete=models.CASCADE)
#     teacher     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     date        = models.DateField()
#     status      = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES)
#     notes       = models.TextField(blank=True, null=True)
#     created_at  = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ['enrollment', 'date']
#         verbose_name = 'Attendance'
#         verbose_name_plural = 'Attendances'

#     def save(self, *args, **kwargs):
#         # Check if this is a new attendance record
#         is_new = self.pk is None
#         old_status = None
        
#         if not is_new:
#             # Get the old status before saving
#             old_status = Attendance.objects.get(pk=self.pk).status

#         super().save(*args, **kwargs)

#         if is_new:
#             # New attendance record
#             if self.status in ['PRESENT', 'ABSENT']:
#                 self.enrollment.remaining_lessons -= 1
#             elif self.status == 'EXCUSED':
#                 self.enrollment.remaining_lessons += 1
#         else:
#             # Status change on existing record
#             if old_status != self.status:
#                 if old_status in ['PRESENT', 'ABSENT'] and self.status == 'EXCUSED':
#                     # Changed from PRESENT/ABSENT to EXCUSED, add back two lessons
#                     self.enrollment.remaining_lessons += 2
#                 elif old_status == 'EXCUSED' and self.status in ['PRESENT', 'ABSENT']:
#                     # Changed from EXCUSED to PRESENT/ABSENT, remove two lessons
#                     self.enrollment.remaining_lessons -= 2

#         self.enrollment.save()