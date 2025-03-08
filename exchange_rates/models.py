from django.db import models
from concurrencies.models import Currency


# Create your models here.

class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency, related_name='exchanges',
                                        on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6,
                                     max_digits=18)
