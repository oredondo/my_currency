from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from .forms import ConverterForm
from .libs.converter import converter
from .models import CurrencyExchangeRate


# Register your models here.
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the CurrencyExchangeRate model.

    Attributes:
        model (Model): The CurrencyExchangeRate model being managed.
        list_display (tuple): Fields to display in the admin list view.

    Provides a custom admin view for currency conversion accessible via a 'converter/' URL.
    """

    model = CurrencyExchangeRate
    list_display = (
        'source_currency',
        'exchanged_currency',
        'valuation_date',
        'rate_value')

    def get_urls(self):
        """
        Extend the default admin URLs with a custom URL for the currency converter view.

        Returns:
            list: A list of URL patterns, including the custom 'converter/' path prepended to the default URLs.

        """
        urls = super().get_urls()
        custom_urls = [
            path('converter/', self.admin_site.admin_view(self.converter_view),
                 name='converter'),
        ]
        return custom_urls + urls

    def converter_view(self, request):
        """
        Handle the currency converter admin view, rendering a form and processing conversion requests.

        Args:
            request (HttpRequest): The HTTP request object containing method and POST data (if any).

        Returns:
            HttpResponse: Renders one of two templates:
                - 'admin/converter_form.html': Displays the form for GET requests or invalid POST submissions.
                - 'admin/converter.html': Displays the conversion result for valid POST submissions.
        """
        if request.method == "POST":
            form = ConverterForm(request.POST)
            if form.is_valid():
                source_currency = form.cleaned_data['source_currency'].code
                amount = form.cleaned_data['amount']
                exchanged_currency = form.cleaned_data['exchanged_currency'].values_list('code', flat=True)
                out = converter(source_currency=source_currency, exchanged_currency=exchanged_currency, value=amount)
                exchange_rate = ""
                for item in out.get('exchanged_currency'):
                    exchange_rate = exchange_rate + f"{item}: {out.get('exchanged_currency')[item]}  ||  "

                result = f"Source_currency {source_currency}: {amount} --> {exchange_rate}"

                return render(request, 'admin/converter.html', {'result': result, 'form': form})
        else:
            form = ConverterForm()

        return render(request, 'admin/converter_form.html', {'form': form})


admin.site.register(CurrencyExchangeRate, CurrencyExchangeRateAdmin)
