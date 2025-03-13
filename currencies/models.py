from django.db import models

# Create your models here.

codes = (('EUR', 'EUR'),
         ('CHF', 'CHF'),
         ('USD', 'USD'),
         ('GBP', 'GBP'))


class Currency(models.Model):
    """
    Model representing a currency with a unique code, name, and symbol.

    Attributes:
        code: A 3-character ISO 4217 currency code (e.g., 'USD').
        name: The full name of the currency (e.g., 'United States Dollar').
        symbol: The symbol associated with the currency (e.g., '$').
    """
    code = models.CharField(max_length=3, choices=codes, unique=True,
                            help_text="ISO 4217 currency code (e.g., 'USD')")
    name = models.CharField(max_length=20, db_index=True,
                            help_text="Full name of the currency (e.g., 'United States Dollar')")
    symbol = models.CharField(max_length=10,
                              help_text="Symbol of the currency (e.g., '$')")

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "currency"
        verbose_name_plural = "currencies"
        ordering = ['code']
