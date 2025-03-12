from datetime import datetime
from unittest.mock import patch

from django.db.models.signals import post_save
from django.test import TestCase

from currencies.models import Currency
from providers.models import Credentials
from currencies.signals import post_save_currency
from exchange_rates.libs.exchange_finder import ExchangeFinder  # Adjust import
from exchange_rates.models import CurrencyExchangeRate


class ExchangeFinderTests(TestCase):
    def setUp(self):
        post_save.disconnect(post_save_currency, sender=Currency)

        # Set up test data in the database
        self.usd = Currency.objects.create(code='USD', name='US Dollar')
        self.eur = Currency.objects.create(code='EUR', name='Euro')
        self.gbp = Currency.objects.create(code='GBP', name='British Pound')
        Credentials.objects.create(name='Mock', url='www.mock.com', token='sdasd', enabled=True, priority=1)
        Credentials.objects.create(name='CurrencyBeacon', url='www.CurrencyBeacon.com', token='sdasd',
                                   enabled=True, priority=2)
        # Sample exchange rates
        CurrencyExchangeRate.objects.create(
            source_currency=self.usd,
            exchanged_currency=self.eur,
            valuation_date=datetime(2025, 1, 1).date(),
            rate_value=0.93
        )
        CurrencyExchangeRate.objects.create(
            source_currency=self.usd,
            exchanged_currency=self.gbp,
            valuation_date=datetime(2025, 1, 1).date(),
            rate_value=0.80
        )

    def test_init_valid_currency(self):
        # Test initialization with a valid source currency
        finder = ExchangeFinder(source_currency='USD', start_date='2025-01-01', end_date='2025-01-02')
        self.assertEqual(finder.code_source_currency, 'USD')
        self.assertEqual(finder.start_date, '2025-01-01')
        self.assertEqual(finder.end_date, '2025-01-02')
        self.assertEqual(finder.source_currency, self.usd)
        self.assertEqual(set(finder.code_target_currency.split(',')), {'EUR', 'GBP'})
        self.assertEqual(len(finder.dates), 2)  # 2025-01-01 and 2025-01-02

    def test_init_invalid_currency(self):
        # Test initialization with an invalid source currency raises DoesNotExist
        with self.assertRaises(Currency.DoesNotExist) as context:
            ExchangeFinder(source_currency='XXX', start_date='2025-01-01', end_date='2025-01-01')
        self.assertEqual(str(context.exception), 'Currency code not found, you need to add')

    def test_date_range_single_day(self):
        # Test _date_range with a single day
        finder = ExchangeFinder(source_currency='USD', start_date='2025-01-01', end_date='2025-01-01')
        dates, current_date = finder._date_range('2025-01-01', '2025-01-01')
        self.assertEqual(len(dates), 1)
        self.assertEqual(dates[0], datetime(2025, 1, 1).date())
        self.assertEqual(current_date, datetime(2025, 1, 1).date())

    def test_date_range_multiple_days(self):
        # Test _date_range with multiple days
        finder = ExchangeFinder(source_currency='USD', start_date='2025-01-01', end_date='2025-01-03')
        dates, current_date = finder._date_range('2025-01-01', '2025-01-03')
        self.assertEqual(len(dates), 3)
        self.assertEqual(dates, [
            datetime(2025, 1, 1).date(),
            datetime(2025, 1, 2).date(),
            datetime(2025, 1, 3).date()
        ])

    def test_get_currency_rates_list_existing_data(self):
        # Test get_currency_rates_list when all data exists
        finder = ExchangeFinder(source_currency='USD', start_date='2025-01-01', end_date='2025-01-01')
        result = finder.get_currency_rates_list()

        expected = {
            '2025-01-01': {
                'EUR': float(0.93),
                'GBP': float(0.80)
            }
        }
        self.assertEqual(result, expected)

    @patch('exchange_rates.libs.exchange_finder.populate')
    def test_get_currency_rates_list_missing_data(self, mock_populate):
        # Test get_currency_rates_list when data is missing and populate is called
        # Add a date with no data
        finder = ExchangeFinder(source_currency='USD', start_date='2025-01-01', end_date='2025-01-02')

        # Mock populate to add missing data
        def side_effect(code_source_currency, start_date, end_date):
            CurrencyExchangeRate.objects.create(
                source_currency=self.usd,
                exchanged_currency=self.eur,
                valuation_date=datetime(2025, 1, 2).date(),
                rate_value=0.94
            )
            CurrencyExchangeRate.objects.create(
                source_currency=self.usd,
                exchanged_currency=self.gbp,
                valuation_date=datetime(2025, 1, 2).date(),
                rate_value=0.81
            )

        mock_populate.side_effect = side_effect

        result = finder.get_currency_rates_list()

        expected = {
            '2025-01-01': {'EUR': 0.93, 'GBP': 0.80},
            '2025-01-02': {'EUR': 0.94, 'GBP': 0.81}
        }
        self.assertEqual(result, expected)
        mock_populate.assert_called_once_with(code_source_currency='USD', start_date='2025-01-01',
                                              end_date='2025-01-02')
