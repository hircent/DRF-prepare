from django.db import models


class Country(models.Model):
    name        = models.CharField(max_length=100)
    code        = models.CharField(max_length=20)
    currency    = models.CharField(max_length=10)

    class Meta:
        db_table = 'countries'
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name
