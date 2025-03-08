from .base import ExchangeRateProvider


class MockProvider(ExchangeRateProvider):
    # This class inherits from MockProvider, implying it’s a concrete implementation
    # of an exchange rate provider. MockProvider likely defines an interface or
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
        Retrieves the historical exchange rate between two currencies for a specific date. By random data.

        :param source_currency: str - The source currency (e.g., "USD").
        :param exchanged_currency: str - The target currency (e.g., "EUR").
        :param valuation_date: str - The date for the exchange rate (likely in YYYY-MM-DD format).
        :return: float - The exchange rate for the target currency.
        """

        return

