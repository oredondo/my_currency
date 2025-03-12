from datetime import datetime
from django.test import TestCase
from unittest.mock import patch, Mock
from currencies.models import Currency
from providers.models import Credentials
from providers.adapters.create_provider import CreateProvider  # Adjust import based on your structure
import requests

class CreateProviderTests(TestCase):
    def setUp(self):
        # Set up test data in the database
        self.usd = Currency.objects.create(code='USD', name='US Dollar')
        self.today = datetime.today().strftime('%Y-%m-%d')

        # Create some credentials
        self.beacon = Credentials.objects.create(
            name='CurrencyBeacon',
            token='test-token',
            url='https://api.currencybeacon.com',
            priority=1,
            enabled=True
        )
        self.mock = Credentials.objects.create(
            name='Mock',
            token=None,
            url=None,
            priority=2,
            enabled=True
        )

    @patch('providers.adapters.create_provider.CurrencyBeaconAdapter')
    def test_create_currency_beacon_success(self, mock_beacon_adapter):
        # Test successful creation of CurrencyBeacon provider
        mock_provider_instance = Mock()
        mock_provider_instance.get_timeseries_rates.return_value = {'2025-01-01': {'EUR': 0.93}}
        mock_beacon_adapter.return_value = mock_provider_instance

        provider_creator = CreateProvider()
        result = provider_creator.create()

        self.assertEqual(result, mock_provider_instance)
        mock_beacon_adapter.assert_called_once_with(token='test-token', url='https://api.currencybeacon.com')
        mock_provider_instance.get_timeseries_rates.assert_called_once_with(
            source_currency='USD', start_date=self.today, end_date=self.today
        )

    @patch('providers.adapters.create_provider.CurrencyBeaconAdapter')
    @patch('providers.adapters.create_provider.MockProvider')
    def test_create_fallback_to_mock(self, mock_mock_provider, mock_beacon_adapter):
        # Test fallback to Mock provider when CurrencyBeacon fails
        mock_beacon_adapter.side_effect = requests.RequestException("API down")
        mock_mock_instance = Mock()
        mock_mock_provider.return_value = mock_mock_instance

        provider_creator = CreateProvider()
        result = provider_creator.create()

        self.assertEqual(result, mock_mock_instance)
        self.assertEqual(Credentials.objects.get(name='CurrencyBeacon').priority, 2)  # Priority changed
        self.assertEqual(Credentials.objects.get(name='Mock').priority, 0)  # Mock now highest
        mock_mock_provider.assert_called_once()

    @patch('providers.adapters.create_provider.CurrencyBeaconAdapter')
    def test_create_currency_beacon_request_exception(self, mock_beacon_adapter):
        # Test handling of RequestException with no other providers
        mock_beacon_adapter.side_effect = requests.RequestException("API down")
        Credentials.objects.filter(name='Mock').delete()  # Remove Mock provider

        provider_creator = CreateProvider()
        with self.assertRaises(ValueError) as context:
            provider_creator.create()
        self.assertEqual(str(context.exception), "There is no Provider, please speak to the administrator")
        self.assertIn('CurrencyBeacon', provider_creator.providers_list)

    @patch('providers.adapters.create_provider.MockProvider')
    def test_create_mock_provider_success(self, mock_mock_provider):
        # Test successful creation of Mock provider when it's the only enabled one
        Credentials.objects.filter(name='CurrencyBeacon').delete()
        mock_mock_instance = Mock()
        mock_mock_provider.return_value = mock_mock_instance

        provider_creator = CreateProvider()
        result = provider_creator.create()

        self.assertEqual(result, mock_mock_instance)
        mock_mock_provider.assert_called_once()

    @patch('providers.adapters.create_provider.MockProvider')
    def test_create_mock_provider_exception(self, mock_mock_provider):
        # Test Mock provider raising an exception with no fallback
        Credentials.objects.filter(name='CurrencyBeacon').delete()
        mock_mock_provider.side_effect = Exception("Mock failed")

        provider_creator = CreateProvider()
        with self.assertRaises(ValueError) as context:
            provider_creator.create()
        self.assertEqual(str(context.exception), "There is no Provider, please speak to the administrator")
        self.assertIn('Mock', provider_creator.providers_list)

    def test_create_no_enabled_providers(self):
        # Test behavior when no enabled providers exist
        Credentials.objects.all().update(enabled=False)

        provider_creator = CreateProvider()
        with self.assertRaises(ValueError) as context:
            provider_creator.create()
        self.assertEqual(str(context.exception), "There is no Provider, please speak to the administrator")
        self.assertEqual(len(provider_creator.providers_list), 0)

    @patch('providers.adapters.create_provider.CurrencyBeaconAdapter')
    def test_change_priority_logic(self, mock_beacon_adapter):
        # Test priority reassignment when CurrencyBeacon fails
        mock_beacon_adapter.side_effect = requests.RequestException("API down")
        # Add a third provider to test priority shuffling
        Credentials.objects.create(name='Backup', token=None, url=None, priority=3, enabled=True)

        provider_creator = CreateProvider()
        result = provider_creator.create()

        # Check priorities after reassignment
        beacon = Credentials.objects.get(name='CurrencyBeacon')
        mock = Credentials.objects.get(name='Mock')
        backup = Credentials.objects.get(name='Backup')
        self.assertEqual(beacon.priority, 3)  # Moved to lowest priority
        self.assertEqual(mock.priority, 0)    # Highest priority now
        self.assertEqual(backup.priority, 1)  # Shifted up
        self.assertIn('CurrencyBeacon', provider_creator.providers_list)

    def tearDown(self):
        # Clean up after tests
        Currency.objects.all().delete()
        Credentials.objects.all().delete()