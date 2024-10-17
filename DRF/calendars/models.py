from django.db import models

from branches.models import Branch

# Create your models here.

class Calendar(models.Model):
    ENTRY_TYPES = [
        ('centre holiday', 'Centre Holiday'),
        ('public holiday', 'Public Holiday'),
        ('event', 'Event'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    year = models.PositiveIntegerField(blank=True,null=True)
    month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)],blank=True,null=True)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_calendars')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.branch.name} ({self.year}-{self.month:02d})"

    def save(self, *args, **kwargs):
        if not self.year:
            self.year = self.start_datetime.year
        if not self.month:
            self.month = self.start_datetime.month
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['year', 'month', 'start_datetime']
        db_table = "calendars"
        verbose_name = "Calendar"
        verbose_name_plural = "Calendars"
