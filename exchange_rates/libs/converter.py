from datetime import datetime

from currencies.models import Currency
from .exchange_finder import ExchangeFinder
from exchange_rates.libs.populate import async_populate_all


def converter(source_currency, exchanged_currency=None, value=None):
    """
    Convert an amount from a source currency to one or more target currencies using exchange rates.

    Args:
        source_currency (str): The currency code of the source currency (e.g., 'USD', 'EUR').
        exchanged_currency (str or list, optional): The currency code(s) of the target currency(ies)
                                                   (e.g., 'EUR', 'GBP'). If None, converts to all
                                                   available currencies except the source.
                                                   Defaults to None.
        value (float, optional): The amount of money to convert from the source currency.
                                 Defaults to None.
    Returns:
        dict: A dictionary containing the conversion results with the following structure:
            - 'date': The date of the conversion (today's date in 'YYYY-MM-DD' format).
            - 'source_currency': A dictionary with the source currency code and the input value.
            - 'exchanged_currency': A dictionary mapping target currency codes to their converted values.
                                    If value is None or invalid, converted values will be None.
    """
    today = datetime.today().strftime('%Y-%m-%d')
    if exchanged_currency is None:
        target_currency = Currency.objects.exclude(code=source_currency).values_list('code', flat=True)
    elif Currency.objects.filter(code__in=exchanged_currency).exists():
        target_currency = exchanged_currency
    else:
        target_currency = []
    result = ExchangeFinder(source_currency, today,
                            today).get_currency_rates_list()

    conversion = {}
    for item in result.get(today):
        if item in target_currency:
            try:
                conversion[item] = result.get(today).get(item) * value
            except TypeError:
                conversion[item] = None
    out = {"date": today,
           "source_currency": {source_currency: value},
           "exchanged_currency": conversion}
    async_populate_all()
    return out
