import random
from abc import ABC
from datetime import timedelta

from .base import ExchangeRateProvider, pre_get_timeseries


class MockProvider(ExchangeRateProvider, ABC):
    # This class inherits from MockProvider, implying it’s a concrete implementation
    # of an exchange rate provider. MockProvider likely defines an interface or
    # abstract methods that this class must implement.

    def __init__(self, token=None, url=None):
        """
        Initializes the adapter with an authentication token and a base URL for the API.

        :param token: str - The authorization token (API key) for CurrencyBeacon.
        :param url: str - The base URL of the API (e.g., "https://api.currencybeacon.com").
        """

        super().__init__()
        self.token = token
        self.url = url

    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        pass

    def _date_range(self, start_date, end_date):
        start_date = start_date.date()
        end_date = end_date.date()
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        return dates, start_date

    def generate_random_rate(self, base_rate):
        variation = random.uniform(-0.05, 0.05)
        return round(base_rate * (1 + variation), 4)

    def get_timeseries_rates(self,
                             source_currency,
                             start_date,
                             end_date):

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
