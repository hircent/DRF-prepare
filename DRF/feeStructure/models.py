from django.db import models
from datetime import datetime
from country.models import Country

class State(models.Model):
    state_name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=20)

    class Meta:
        db_table = 'states'
        verbose_name = 'State'
        verbose_name_plural = 'States'

    def __str__(self):
        return self.state_name

class Tier(models.Model):
    country         = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='tiers')
    tier_level      = models.PositiveIntegerField()
    year            = models.PositiveIntegerField(default=datetime.now().year)
    name            = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tiers'
        verbose_name = 'Tier'
        verbose_name_plural = 'Tiers'
    
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
        ('KIDDO', 'KIDDO'),
        ('KIDS', 'KIDS'),
        ('SUPERKIDS', 'SUPERKIDS'),
    ]

    tier            = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='grades')
    grade_level     = models.IntegerField(choices=GRADE_CHOICES)
    category        = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grades'
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        unique_together = ['tier', 'grade_level','category']
        
    def __str__(self):
        return str(self.grade_level)

