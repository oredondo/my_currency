from datetime import datetime

import requests

from currencies.models import Currency
from providers.models import Credentials
from .currency_beacon import CurrencyBeaconAdapter
from .mock_provider import MockProvider


class CreateProvider(object):
    """
    Factory class to create and manage currency provider instances.
    Follows the Factory pattern to instantiate appropriate provider adapters.
    """

    def __init__(self):
        self.today = datetime.today().strftime('%Y-%m-%d')
        self.providers_list = []

    def create(self):
        """
        Creates and returns a provider instance based on available credentials.
        Check if the provider works if not change the priority.

        Returns:
            Provider instance if successful, None otherwise
        """

        for provider in Credentials.objects.filter(enabled=True).order_by('priority'):
            if provider.name == 'CurrencyBeacon':
                try:
                    prov = CurrencyBeaconAdapter(token=provider.token,
                                                 url=provider.url)
                    currency = Currency.objects.all().first()
                    prov.get_timeseries_rates(source_currency=currency.code, start_date=self.today,
                                              end_date=self.today)
                    return prov
                except requests.RequestException:
                    return self._change_priority(provider)
            elif provider.name == 'Mock':
                try:
                    try:
                        return MockProvider()
                    except Exception:
                        return self._change_priority(provider)
                except requests.RequestException:
                    raise ValueError("There is no Provider, please speak to the administrator")
        raise ValueError("There is no Provider, please speak to the administrator")

    def _change_priority(self, provider):
        """
        Adjusts provider priorities and attempts to create a new provider.

        Args:
            provider: Credentials instance to modify

        Returns:
            Provider instance if successful, None otherwise
        """
        if provider.name in self.providers_list:
            raise ValueError("There is no Provider, please speak to the administrator")

        self.providers_list.append(provider.name)
        maxi = max(Credentials.objects.values_list('priority', flat=True).distinct())
        i = 0
        ch = None
        for provider_item in Credentials.objects.order_by('priority'):
            if provider_item.priority == provider.priority:
                if Credentials.objects.filter(priority=provider_item.priority).exists():
                    ch = Credentials.objects.get(priority=provider_item.priority)
                    ch.priority = i
                    ch.save()
                provider_item.priority = maxi + 1
            elif ch != provider_item:
                provider_item.priority = i
            i = i + 1
            provider_item.save()
        return self.create()
