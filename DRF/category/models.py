from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Kiddo', 'Kiddo'),
        ('Kids', 'Kids'),
        ('Superkids', 'Superkids'),
    ]
    
    name        = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    label       = models.CharField(max_length=100,blank=True, null=True)
    year        = models.PositiveIntegerField(default=timezone.now().year)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

        unique_together = ('name', 'year')
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.name + ' ' + str(self.year)
        super().save(*args, **kwargs)
    

class Theme(models.Model):
    name            = models.CharField(max_length=100)
    order           = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1), MaxValueValidator(12)])
    category        = models.ForeignKey(Category, related_name='themes', on_delete=models.CASCADE)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'themes'
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'
        ordering = ['order']
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['category', 'name'],
        #         name='unique_theme_per_category'
        #     )
        # ]
    
    def __str__(self):
        return self.name
    
class ThemeLesson(models.Model):
    theme           = models.ForeignKey(Theme, related_name='theme_lessons', on_delete=models.CASCADE)
    name            = models.CharField(max_length=100)
    order           = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1), MaxValueValidator(4)])
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'theme_lessons'
        verbose_name = 'Theme Lesson'
        verbose_name_plural = 'Theme Lessons'
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Grade(models.Model):
    GRADE_CHOICES = [
        (1, 'Grade 1'),
        (2, 'Grade 2'),
        (3, 'Grade 3'),
        (4, 'Grade 4'),
        (5, 'Grade 5'),
        (6, 'Grade 6'),
    ]

    CATEGORY_CHOICES = [
        ('KIDDO', 'Kiddo'),
        ('KIDS', 'Kids'),
        ('SUPERKIDS', 'Superkids'),
    ]
    
    grade_level     = models.IntegerField(choices=GRADE_CHOICES, unique=True)
    category        = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grades'
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        
    def __str__(self):
        return str(self.grade_level)
    