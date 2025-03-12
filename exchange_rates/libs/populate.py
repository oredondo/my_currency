import threading
from datetime import datetime, timedelta

from currencies.models import Currency
from exchange_rates.models import CurrencyExchangeRate
from providers.adapters.create_provider import CreateProvider


def populate(code_source_currency, start_date, end_date=None):
    """
    Populate the database with currency exchange rates for a source currency over a date range.

    Args:
        code_source_currency (str): The currency code of the source currency (e.g., 'USD', 'EUR').
        start_date (str): The start date for fetching exchange rates in 'YYYY-MM-DD' format.
        end_date (str, optional): The end date for fetching exchange rates in 'YYYY-MM-DD' format.
                                  Defaults to None, in which case today's date is used.
    """
    provider = CreateProvider().create()
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    result = provider.get_timeseries_rates(code_source_currency, start_date,
                                           end_date)

    for day in result:
        for money in result.get(day):
            if not CurrencyExchangeRate.objects.filter(source_currency=Currency.objects.get(code=code_source_currency),
                                                       valuation_date=datetime.strptime(day, "%Y-%m-%d").date(),
                                                       exchanged_currency=Currency.objects.get(code=money)):
                CurrencyExchangeRate.objects.create(source_currency=Currency.objects.get(code=code_source_currency),
                                                    valuation_date=datetime.strptime(day, "%Y-%m-%d").date(),
                                                    exchanged_currency=Currency.objects.get(code=money),
                                                    rate_value=result.get(day).get(money))


def async_populate_all():
    """
    Asynchronously update exchange rates for all currencies in the database.
    """
    for item in Currency.objects.values_list('code', flat=True):
        date = CurrencyExchangeRate.objects.filter(source_currency=Currency.objects.get(code=item)).values_list(
            'valuation_date', flat=True).order_by('-valuation_date').first()
        if not date:
            date = datetime.now() - timedelta(days=365)
        if date.strftime("%Y-%m-%d") != datetime.now().strftime("%Y-%m-%d"):
            thread = threading.Thread(target=populate, args=(item, date.strftime("%Y-%m-%d")))
            thread.start()
