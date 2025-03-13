from abc import ABC

import requests

from .base import ExchangeRateProvider, pre_get_timeseries


class CurrencyBeaconAdapter(ExchangeRateProvider, ABC):
    """
    Adapter class for CurrencyBeacon API implementing the ExchangeRateProvider interface.
    Handles exchange rate retrieval for specific dates and time series.

    """
    def __init__(self, token, url):
        """
        Initialize the CurrencyBeacon adapter with API credentials.

        Args:
            token: API authentication token
            url: Base URL for CurrencyBeacon API endpoint

        """

        super().__init__()
        self.token = token
        self.url = url

    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        """
        Fetch historical exchange rate for a specific date.

        Args:
            source_currency: Base currency code ("USD")
            exchanged_currency: Target currency code ("EUR")
            valuation_date: Date in YYYY-MM-DD format

        Returns:
            Exchange rate as a float

        """

        url = (f"{self.url}"
               f"/v1/historical?base={source_currency}&date={valuation_date}&symbols={exchanged_currency}")
        response = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        response.raise_for_status()
        data = response.json()
        return data.get("response").get(valuation_date).get(exchanged_currency)

    def get_timeseries_rates(self,
                             source_currency,
                             start_date,
                             end_date):
        """
        Fetch exchange rate time series between two dates.

        Args:
            source_currency: Base currency code
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary of date-rate pairs

        """
        start, end, exchanged_currency = pre_get_timeseries(source_currency,
                                                            start_date,
                                                            end_date)

        try:
            url = (f"{self.url}"
                   f"/v1/timeseries?base={source_currency.upper()}&"
                   f"symbols={exchanged_currency.upper()}&start_date={start_date}&end_date={end_date}")
            response = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                return data.get("response")
            raise ValueError("Invalid response format from API")

        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to retrieve exchange rates from API: {e}")
        except (KeyError, ValueError) as e:
            raise Exception(f"Failed to retrieve exchange rates from key Value: {e}")
