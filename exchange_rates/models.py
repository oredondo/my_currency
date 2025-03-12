from django.db import models

from currencies.models import Currency


class CurrencyExchangeRate(models.Model):
    """
        A Django model representing an exchange rate between two currencies on a specific date.

        Attributes:
            source_currency (ForeignKey): The currency from which the exchange rate is calculated.
            exchanged_currency (ForeignKey): The currency to which the exchange rate applies.
            valuation_date (DateField): The date the exchange rate is valid for.
            rate_value (DecimalField): The exchange rate value, with high precision.
    """
    source_currency = models.ForeignKey(Currency, related_name='exchanges',
                                        on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6,
                                     max_digits=18)
