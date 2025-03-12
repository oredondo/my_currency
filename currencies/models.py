from django.db import models

# Create your models here.

codes = (('EUR', 'EUR'),
         ('CHF', 'CHF'),
         ('USD', 'USD'),
         ('GBP', 'GBP'))


class Currency(models.Model):
    code = models.CharField(max_length=3, choices=codes, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.code
