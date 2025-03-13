from django.contrib import admin

from .models import Currency


# Register your models here.
class CurrencyAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Currency model.
    Customizes the display and behavior of Currency instances in the Django admin interface.
    """
    model = Currency
    list_display = (
        'code',
        'name',
        'symbol')
    ordering = ('code',)


admin.site.register(Currency, CurrencyAdmin)
