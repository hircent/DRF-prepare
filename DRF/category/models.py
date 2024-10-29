from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('KIDDOS', 'Kiddos'),
        ('KIDS', 'Kids'),
        ('SUPERKIDS', 'Superkids'),
    ]
    
    name        = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    label       = models.CharField(max_length=100,blank=True, null=True)
    year        = models.PositiveIntegerField(default=timezone.now().year)
    is_active   = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

        unique_together = ('name', 'year')
        
    def __str__(self):
        return self.label
    
    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.name + ' ' + str(self.year)
        super().save(*args, **kwargs)
    

class Theme(models.Model):
    name        = models.CharField(max_length=100)
    category    = models.ForeignKey(Category, related_name='themes', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'],
                name='unique_theme_per_category'
            )
        ]
    

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
        ('KIDDOS', 'Kiddos'),
        ('KIDS', 'Kids'),
        ('SUPERKIDS', 'Superkids'),
    ]
    
    grade_level     = models.IntegerField(choices=GRADE_CHOICES, unique=True)
    category        = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
    