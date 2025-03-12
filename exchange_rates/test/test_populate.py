from datetime import datetime
from unittest.mock import patch, Mock

from django.test import TestCase

from currencies.models import Currency
from exchange_rates.libs.populate import populate  # Adjust import based on your structure
from exchange_rates.models import CurrencyExchangeRate


class PopulateFunctionTests(TestCase):
    def setUp(self):
        # Set up test data in the database
        self.usd = Currency.objects.create(code='USD', name='US Dollar')
        self.eur = Currency.objects.create(code='EUR', name='Euro')
        self.gbp = Currency.objects.create(code='GBP', name='British Pound')
        self.start_date = '2025-01-01'
        self.today = datetime.today().strftime('%Y-%m-%d')

    @patch('exchange_rates.libs.populate.CreateProvider')
    def test_populate_successful_creation_with_end_date(self, mock_create_provider):
        # Test successful population with explicit end_date
        mock_provider_instance = Mock()
        mock_provider_instance.get_timeseries_rates.return_value = {
            '2025-01-01': {'EUR': 0.93, 'GBP': 0.80},
            '2025-01-02': {'EUR': 0.94, 'GBP': 0.81}
        }
        mock_create_provider.return_value.create.return_value = mock_provider_instance

        populate(code_source_currency='USD', start_date=self.start_date, end_date='2025-01-02')

        # Verify the records were created
        self.assertEqual(CurrencyExchangeRate.objects.count(), 4)
        rate_eur_01 = CurrencyExchangeRate.objects.get(source_currency=self.usd, exchanged_currency=self.eur,
                                                       valuation_date='2025-01-01')
        self.assertEqual(float(rate_eur_01.rate_value), 0.93)
        rate_gbp_02 = CurrencyExchangeRate.objects.get(source_currency=self.usd, exchanged_currency=self.gbp,
                                                       valuation_date='2025-01-02')
        self.assertEqual(float(rate_gbp_02.rate_value), 0.81)
        mock_provider_instance.get_timeseries_rates.assert_called_once_with('USD', self.start_date, '2025-01-02')

    @patch('exchange_rates.libs.populate.CreateProvider')
    def test_populate_successful_creation_default_end_date(self, mock_create_provider):
        # Test successful population with default end_date (today)
        mock_provider_instance = Mock()
        mock_provider_instance.get_timeseries_rates.return_value = {
            '2025-01-01': {'EUR': 0.93, 'GBP': 0.80}
        }
        mock_create_provider.return_value.create.return_value = mock_provider_instance

        populate(code_source_currency='USD', start_date=self.start_date)

        # Verify the records were created
        self.assertEqual(CurrencyExchangeRate.objects.count(), 2)
        rate_eur_01 = CurrencyExchangeRate.objects.get(source_currency=self.usd, exchanged_currency=self.eur,
                                                       valuation_date='2025-01-01')
        self.assertEqual(float(rate_eur_01.rate_value), 0.93)
        mock_provider_instance.get_timeseries_rates.assert_called_once_with('USD', self.start_date, self.today)

    @patch('exchange_rates.libs.populate.CreateProvider')
    def test_populate_existing_records(self, mock_create_provider):
        # Test that existing records are not duplicated
        CurrencyExchangeRate.objects.create(
            source_currency=self.usd,
            exchanged_currency=self.eur,
            valuation_date='2025-01-01',
            rate_value=0.93
        )

        mock_provider_instance = Mock()
        mock_provider_instance.get_timeseries_rates.return_value = {
            '2025-01-01': {'EUR': 0.93, 'GBP': 0.80}  # EUR already exists
        }
        mock_create_provider.return_value.create.return_value = mock_provider_instance

        populate(code_source_currency='USD', start_date=self.start_date, end_date='2025-01-01')

        # Only GBP should be added, EUR should remain unchanged
        self.assertEqual(CurrencyExchangeRate.objects.count(), 2)
        rate_gbp = CurrencyExchangeRate.objects.get(source_currency=self.usd, exchanged_currency=self.gbp,
                                                    valuation_date='2025-01-01')
        self.assertEqual(float(rate_gbp.rate_value), 0.80)
        self.assertEqual(
            CurrencyExchangeRate.objects.filter(source_currency=self.usd, exchanged_currency=self.eur).count(), 1)

    @patch('exchange_rates.libs.populate.CreateProvider')
    def test_populate_missing_currency(self, mock_create_provider):
        # Test behavior when a target currency code from provider doesn't exist
        mock_provider_instance = Mock()
        mock_provider_instance.get_timeseries_rates.return_value = {
            '2025-01-01': {'XXX': 1.5}  # XXX doesn't exist in Currency table
        }
        mock_create_provider.return_value.create.return_value = mock_provider_instance

        with self.assertRaises(Currency.DoesNotExist) as context:
            populate(code_source_currency='USD', start_date=self.start_date, end_date='2025-01-01')
        self.assertIn('Currency matching query does not exist', str(context.exception))
        self.assertEqual(CurrencyExchangeRate.objects.count(), 0)  # No records created

    @patch('exchange_rates.libs.populate.CreateProvider')
    def test_populate_empty_result(self, mock_create_provider):
        # Test behavior when provider returns an empty result
        mock_provider_instance = Mock()
        mock_provider_instance.get_timeseries_rates.return_value = {}
        mock_create_provider.return_value.create.return_value = mock_provider_instance

        populate(code_source_currency='USD', start_date=self.start_date, end_date='2025-01-01')

        self.assertEqual(CurrencyExchangeRate.objects.count(), 0)  # No records should be created
        mock_provider_instance.get_timeseries_rates.assert_called_once_with('USD', self.start_date, '2025-01-01')

    @patch('exchange_rates.libs.populate.CreateProvider')
    def test_populate_invalid_source_currency(self, mock_create_provider):
        # Test behavior when source currency doesn't exist
        mock_provider_instance = Mock()
        mock_provider_instance.get_timeseries_rates.return_value = {
            '2025-01-01': {'EUR': 0.93}
        }
        mock_create_provider.return_value.create.return_value = mock_provider_instance

        with self.assertRaises(Currency.DoesNotExist) as context:
            populate(code_source_currency='XXX', start_date=self.start_date, end_date='2025-01-01')
        self.assertIn('Currency matching query does not exist', str(context.exception))
        self.assertEqual(CurrencyExchangeRate.objects.count(), 0)  # No records created

    def tearDown(self):
        # Clean up after tests
        Currency.objects.all().delete()
        CurrencyExchangeRate.objects.all().delete()
