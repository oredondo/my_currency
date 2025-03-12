from datetime import datetime
from datetime import timedelta

from currencies.models import Currency
from exchange_rates.libs.populate import populate, async_populate_all
from exchange_rates.models import CurrencyExchangeRate


class ExchangeFinder(object):
    """
    A class to find and retrieve currency exchange rates between a source currency and target currencies
    over a specified date range.
    """

    def __init__(self, source_currency, start_date, end_date):
        """
        Initialize the ExchangeFinder with a source currency and date range.

        Args:
            source_currency (str): The currency code of the source currency (e.g., 'USD', 'EUR').
            start_date (str): The start date for the exchange rate query in 'YYYY-MM-DD' format.
            end_date (str): The end date for the exchange rate query in 'YYYY-MM-DD' format.

        Raises:
            Currency.DoesNotExist: If the source_currency code does not exist in the Currency model.
        """
        self.code_source_currency = source_currency
        self.start_date = start_date
        self.end_date = end_date
        try:
            self.source_currency = Currency.objects.get(code=source_currency)
            self.target_currency = Currency.objects.exclude(code=source_currency).values_list('id')
            self.code_target_currency = ",".join(Currency.objects.exclude(
                code=source_currency).values_list('code', flat=True))
        except Currency.DoesNotExist:
            raise Currency.DoesNotExist('Currency code not found, you need to add')
        self.dates, self.current_date = self._date_range(start_date, end_date)

    def _date_range(self, start_date, end_date):
        """
        Generate a list of dates between start_date and end_date.

        Args:
            start_date (str): The start date in 'YYYY-MM-DD' format.
            end_date (str): The end date in 'YYYY-MM-DD' format.

        Returns:
            tuple: A tuple containing:
                - list: A list of date objects between start_date and end_date (inclusive).
                - date: The start_date as a date object.

        Raises:
            ValueError: If the date format is invalid (not 'YYYY-MM-DD').
        """
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format, expected YYYY-MM-DD")
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        return dates, start_date

    def get_currency_rates_list(self):
        """
        Retrieve a dictionary of exchange rates for the source currency against target currencies
        over the specified date range.

        Returns:
            dict: A dictionary where keys are dates in 'YYYY-MM-DD' format and values are dictionaries
                  mapping target currency codes to their exchange rates (as floats).

        """
        out = {}
        end = True
        while end:
            dates_set = set(self.dates)
            target_currency = set(self.code_target_currency.split(','))
            existing_dates = set(
                CurrencyExchangeRate.objects.filter(
                    source_currency=self.source_currency,
                    exchanged_currency__in=self.target_currency,
                    valuation_date__in=self.dates
                ).values_list('valuation_date', flat=True).distinct()
            )
            existing_target_currency = set(
                CurrencyExchangeRate.objects.filter(
                    source_currency=self.source_currency,
                    exchanged_currency__in=self.target_currency,
                    valuation_date__in=self.dates
                ).values_list('exchanged_currency__code', flat=True).distinct()
            )

            if existing_dates == dates_set and target_currency == existing_target_currency:
                exchanged_currency = CurrencyExchangeRate.objects.filter(source_currency=self.source_currency,
                                                                         exchanged_currency__in=self.target_currency,
                                                                         valuation_date__in=self.dates).order_by(
                    'valuation_date')
                for item in exchanged_currency:
                    if out.get(item.valuation_date.strftime("%Y-%m-%d")):
                        out[item.valuation_date.strftime("%Y-%m-%d")].update({
                            item.exchanged_currency.code: float(item.rate_value)})
                    else:
                        out.update(
                            {item.valuation_date.strftime("%Y-%m-%d"): {
                                item.exchanged_currency.code: float(item.rate_value)}})
                end = False
            else:
                populate(code_source_currency=self.code_source_currency, start_date=self.start_date,
                         end_date=self.end_date)
        async_populate_all()
        return out
