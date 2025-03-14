from django.apps import AppConfig


class ConcurrenciesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currencies'

    def ready(self):
        import currencies.signals
