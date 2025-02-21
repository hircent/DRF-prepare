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
        return self.theme.name + ' ' + self.name + ' ' + str(self.theme.category.year)

    