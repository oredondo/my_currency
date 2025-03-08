from django.contrib import admin

from .models import CurrencyExchangeRate


# Register your models here.
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    model = CurrencyExchangeRate
    list_display = (
        'source_currency',
        'exchanged_currency',
        'valuation_date',
        'rate_value')


admin.site.register(CurrencyExchangeRate, CurrencyExchangeRateAdmin)
