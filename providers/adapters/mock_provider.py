import random
from abc import ABC
from datetime import timedelta

from .base import ExchangeRateProvider, pre_get_timeseries


class MockProvider(ExchangeRateProvider, ABC):
    """
        Mock implementation of ExchangeRateProvider for testing purposes.
        Generates random exchange rates instead of fetching from an API.
    """
    def __init__(self, token=None, url=None):
        """
        Initialize the mock provider. Token and URL are optional as this is a mock.

        Args:
            token: Optional API token (not used in mock)
            url: Optional API URL (not used in mock)
        """

        super().__init__()
        self.token = token
        self.url = url

    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        pass

    def _date_range(self, start_date, end_date):
        """
        Generate a list of dates between start and end dates.

        Args:
            start_date: Starting datetime object
            end_date: Ending datetime object

        Returns:
            Tuple containing list of dates and normalized start_date
        """
        start_date = start_date.date()
        end_date = end_date.date()
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        return dates, start_date

    def generate_random_rate(self, base_rate):
        """
        Generate a random exchange rate with small variation from base rate.

        Args:
            base_rate: Base rate to vary from

        Returns:
            Random rate rounded to 4 decimal places
        """
        variation = random.uniform(-0.05, 0.05)
        return round(base_rate * (1 + variation), 4)

    def get_timeseries_rates(self,
                             source_currency,
                             start_date,
                             end_date):
        """
        Generate mock time series exchange rates for given date range.

        Args:
            source_currency: Base currency code
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with date strings as keys and currency-rate pairs as values
        """

        start, end, exchanged_currency = pre_get_timeseries(source_currency, start_date, end_date)

        dates, start_date = self._date_range(start, end)

        response = {}
        for date in dates:
            for exchanged in exchanged_currency.split(','):
                if response.get(date.strftime("%Y-%m-%d")) is None:
                    response.update({date.strftime("%Y-%m-%d"): {exchanged: self.generate_random_rate(1)}})
                else:
                    response[date.strftime("%Y-%m-%d")].update({exchanged: self.generate_random_rate(1)})
        return response
