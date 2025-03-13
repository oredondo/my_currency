from django.urls import path

from .views import ExchangeRateListView, ConverterView

urlpatterns_exchange = [
    path('concurrency_rate_list/',
         ExchangeRateListView.as_view(), name='concurrency_rate_list'),
    path('convert_amount/',
         ConverterView.as_view(), name='convert_amount'), ]
