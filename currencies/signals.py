

from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Currency
from exchange_rates.lib.populate import async_populate_all

@receiver(post_save, sender=Currency)
def post_save_currency(sender, instance, created, **kwargs):
    if created:
        async_populate_all()

