from .currency_beacon import CurrencyBeaconAdapter
from ..models import Credentials


class CreateProvider(object):
    @staticmethod
    def create():
        for provider in Credentials.objects.order_by('priority'):
            return CurrencyBeaconAdapter(token=provider.token,
                                         url=provider.user)
        else:
            raise ValueError("There is no Provider, please speak to the administrator")

    @staticmethod
    def _change_priority(provider):
        total = Credentials.objects.count()
        i = 0
        for provider_item in Credentials.objects.order_by('priority'):
            if provider_item.priority == provider.priority:
                provider_item.priority = total - 1
            else:
                provider_item.priority = i
            i = i + 1
