from datetime import datetime

import requests
from concurrencies.models import Currency

from .base import ExchangeRateProvider


class CurrencyBeaconAdapter(ExchangeRateProvider):
    # This class inherits from ExchangeRateProvider, implying it’s a concrete implementation
    # of an exchange rate provider. ExchangeRateProvider likely defines an interface or
    # abstract methods that this class must implement.

    def __init__(self, token, url):
        """
        Initializes the adapter with an authentication token and a base URL for the API.

        :param token: str - The authorization token (API key) for CurrencyBeacon.
        :param url: str - The base URL of the API (e.g., "https://api.currencybeacon.com").
        """

        super().__init__()
        self.token = token
        self.url = url

    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        """
        Retrieves the historical exchange rate between two currencies for a specific date.

        :param source_currency: str - The source currency (e.g., "USD").
        :param exchanged_currency: str - The target currency (e.g., "EUR").
        :param valuation_date: str - The date for the exchange rate (likely in YYYY-MM-DD format).
        :return: float - The exchange rate for the target currency.
        """

        url = (f"{self.url}"
               f"/v1/historical?base={source_currency}&date={valuation_date}&symbols={exchanged_currency}")
        response = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        response.raise_for_status()
        data = response.json()
        return data.get("rates").get(exchanged_currency)

    def get_timeseries_rates(self,
                             source_currency,
                             start_date,
                             end_date):
        """
        Get exchange rates between two currencies over a date range.

        :param source_currency: str - The base currency code (e.g., "USD")
        :param exchanged_currency: str - The target currency code (e.g., "EUR" or, "ADA,CHF")
        :param start_date: str - Start date in YYYY-MM-DD format
        :param end_date: str - End date in YYYY-MM-DD format
        :return: Dict[str, float] or None - Dictionary with dates as keys and rates as values,
                                           or None if the request fails
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                raise ValueError("start_date must be earlier than end_date")
        except ValueError as e:
            raise ValueError(f"Dates must be in YYYY-MM-DD format: {e}")
        try:
            exchanged_currency = ",".join(Currency.objects.filter(code__iexact=source_currency).values_list('code', flat=True))
        except Currency.DoesNotExist:
            raise ValueError(f"Currency codes does not exist, you need to add")

        try:
            url = (f"{self.url}"
                   f"/v1/timeseries?base={source_currency.upper()}&"
                   f"symbols={exchanged_currency.upper()}&start_date={start_date}&start_date={end_date}")
            response = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                return data.get("response")
            raise ValueError("Invalid response format from API")

        except requests.RequestException as e:
            raise Exception(f"Failed to retrieve exchange rates from API: {e}")
        except (KeyError, ValueError) as e:
            raise Exception(f"Failed to retrieve exchange rates from key Value: {e}")
