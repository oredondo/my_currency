from django.db.models.signals import post_save
from django.dispatch import receiver

from exchange_rates.libs.populate import async_populate_all
from .models import Currency


@receiver(post_save, sender=Currency)
def post_save_currency(sender, instance, created, **kwargs):
    """
    Signal handler triggered after a Currency instance is saved.

    If the Currency instance was newly created, triggers an asynchronous task
    to populate all related data.
    """
    if created:
        async_populate_all()
