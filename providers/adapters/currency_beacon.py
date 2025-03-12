from abc import ABC

import requests

from .base import ExchangeRateProvider, pre_get_timeseries


class CurrencyBeaconAdapter(ExchangeRateProvider, ABC):
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
        return data.get("response").get(valuation_date).get(exchanged_currency)

    def get_timeseries_rates(self,
                             source_currency,
                             start_date,
                             end_date):
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
