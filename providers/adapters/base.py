from abc import ABC, abstractmethod
from datetime import datetime

from currencies.models import Currency


def pre_get_timeseries(source_currency,
                       start_date,
                       end_date):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if start > end:
            raise ValueError("start_date must be earlier than end_date")
    except ValueError as e:
        raise ValueError(f"Dates must be in YYYY-MM-DD format: {e}")
    try:
        exchanged_currency = ",".join(Currency.objects.exclude(code=source_currency.upper()
                                                               ).values_list('code', flat=True))
    except Currency.DoesNotExist:
        raise Currency.DoesNotExist(f"Currency codes does not exist, you need to add")
    return start, end, exchanged_currency


class ExchangeRateProvider(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        pass

    @abstractmethod
    def get_timeseries_rates(self, source_currency, exchanged_currency, valuation_date):
        """
            Get exchange rates between two currencies over a date range.

            :param source_currency: str - The base currency code (e.g., "USD")
            :param exchanged_currency: str - The target currency code (e.g., "EUR" or, "ADA,CHF")
            :param start_date: str - Start date in YYYY-MM-DD format
            :param end_date: str - End date in YYYY-MM-DD format
            :return: Dict[str, float] or None - Dictionary with dates as keys and rates as values,
                                               or None if the request fails
            """
        pass
