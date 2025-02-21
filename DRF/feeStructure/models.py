from django.db import models

class Tier(models.Model):
    tier_level      = models.PositiveIntegerField()
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
    
class TierGradeFees(models.Model):
    tier            = models.ForeignKey(Tier, related_name='fees', on_delete=models.CASCADE)
    grade           = models.ForeignKey(Grade, related_name='fees', on_delete=models.CASCADE)
    fee             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tier_grade_fees'
        verbose_name = 'Tier Grade Fee'
        verbose_name_plural = 'Tier Grade Fees'
        
    def __str__(self):
        return self.tier.name + ' ' + self.grade.grade_level + ' ' + str(self.fee)
