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
    student             = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='enrolments')
    branch              = models.ForeignKey(Branch, on_delete=models.CASCADE)
    grade               = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    enrollment_date     = models.DateTimeField(auto_now_add=True)
    is_active           = models.BooleanField(default=True)
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
    class_instance      = models.ForeignKey(Class, on_delete=models.CASCADE,related_name='lessons')
    students            = models.ManyToManyField(StudentEnrolment)
    # theme               = models.ForeignKey(Theme, on_delete=models.CASCADE)
    # lesson_number       = models.PositiveIntegerField()  # 1-4 for each theme
    # lesson_name         = models.CharField(max_length=100)
    lesson_date         = models.DateField()
    # theme_order         = models.PositiveIntegerField()  # 1-12 for tracking theme sequence
    # is_completed        = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'class_lessons'
        ordering = ['-lesson_date']
        verbose_name = 'Class Lesson'
        verbose_name_plural = 'Class Lessons'
        unique_together = ['class_instance', 'lesson_date']

    def __str__(self):
        return self.lesson_content

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