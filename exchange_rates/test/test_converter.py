from datetime import datetime
from django.test import TestCase
from unittest.mock import patch, Mock
from currencies.models import Currency
from exchange_rates.lib.converter import converter  # Adjust import based on your structure

class ConverterFunctionTests(TestCase):
    def setUp(self):
        # Set up test data in the database
        self.currency_usd = Currency.objects.create(code='USD', name='US Dollar')
        self.currency_eur = Currency.objects.create(code='EUR', name='Euro')
        self.currency_gbp = Currency.objects.create(code='GBP', name='British Pound')
        self.today = datetime.today().strftime('%Y-%m-%d')

    @patch('exchange_rates.lib.converter.ExchangeFinder')  # Mock ExchangeFinder
    @patch('exchange_rates.lib.converter.async_populate_all')  # Mock async_populate_all
    def test_converter_single_currency(self, mock_populate, mock_exchange_finder):
        # Test conversion to a single target currency with valid parameters
        mock_instance = mock_exchange_finder.return_value
        mock_instance.get_currency_rates_list.return_value = {
            self.today: {'USD': 1.0, 'EUR': 0.93, 'GBP': 0.80}
        }

        result = converter(source_currency='USD', exchanged_currency=['EUR'], value=100)

        expected = {
            "date": self.today,
            "source_currency": {"USD": 100},
            "exchanged_currency": {"EUR": 93.0}  # 100 * 0.93
        }
        self.assertEqual(result, expected)
        mock_exchange_finder.assert_called_once_with('USD', self.today, self.today)
        mock_populate.assert_called_once()

    @patch('exchange_rates.lib.converter.ExchangeFinder')
    @patch('exchange_rates.lib.converter.async_populate_all')
    def test_converter_all_currencies(self, mock_populate, mock_exchange_finder):
        # Test conversion to all currencies when exchanged_currency is None
        mock_instance = mock_exchange_finder.return_value
        mock_instance.get_currency_rates_list.return_value = {
            self.today: {'USD': 1.0, 'EUR': 0.93, 'GBP': 0.80}
        }

        result = converter(source_currency='USD', value=100)

        expected = {
            "date": self.today,
            "source_currency": {"USD": 100},
            "exchanged_currency": {
                "EUR": 93.0,  # 100 * 0.93
                "GBP": 80.0   # 100 * 0.80
            }
        }
        self.assertEqual(result, expected)
        mock_exchange_finder.assert_called_once_with('USD', self.today, self.today)
        mock_populate.assert_called_once()

    @patch('exchange_rates.lib.converter.ExchangeFinder')
    @patch('exchange_rates.lib.converter.async_populate_all')
    def test_converter_invalid_exchanged_currency(self, mock_populate, mock_exchange_finder):
        # Test conversion with an invalid exchanged_currency code
        mock_instance = mock_exchange_finder.return_value
        mock_instance.get_currency_rates_list.return_value = {
            self.today: {'USD': 1.0, 'EUR': 0.93, 'GBP': 0.80}
        }

        result = converter(source_currency='USD', exchanged_currency='XXX', value=100)

        expected = {
            "date": self.today,
            "source_currency": {"USD": 100},
            "exchanged_currency": {}  # Empty because 'XXX' doesn't exist
        }
        self.assertEqual(result, expected)
        mock_exchange_finder.assert_called_once_with('USD', self.today, self.today)
        mock_populate.assert_called_once()

    @patch('exchange_rates.lib.converter.ExchangeFinder')
    @patch('exchange_rates.lib.converter.async_populate_all')
    def test_converter_no_value(self, mock_populate, mock_exchange_finder):
        # Test behavior when value is None (should still multiply by None, resulting in None or error handling)
        mock_instance = mock_exchange_finder.return_value
        mock_instance.get_currency_rates_list.return_value = {
            self.today: {'USD': 1.0, 'EUR': 0.93, 'GBP': 0.80}
        }

        result = converter(source_currency='USD', exchanged_currency=['EUR'], value=None)

        expected = {
            "date": self.today,
            "source_currency": {"USD": None},
            "exchanged_currency": {"EUR": None}  # None * 0.93 = None
        }
        self.assertEqual(result, expected)
        mock_exchange_finder.assert_called_once_with('USD', self.today, self.today)
        mock_populate.assert_called_once()

    @patch('exchange_rates.lib.converter.ExchangeFinder')
    @patch('exchange_rates.lib.converter.async_populate_all')
    def test_converter_exchange_finder_exception(self, mock_populate, mock_exchange_finder):
        # Test that an exception in ExchangeFinder propagates up
        mock_exchange_finder.side_effect = Exception("Exchange rate fetch failed")

        with self.assertRaises(Exception) as context:
            converter(source_currency='USD', exchanged_currency='EUR', value=100)
        self.assertEqual(str(context.exception), "Exchange rate fetch failed")
        mock_populate.assert_not_called()  # Shouldn't be called if exception occurs

    def test_converter_no_currencies_in_db(self):
        Currency.objects.all().delete()

        with patch('exchange_rates.lib.converter.ExchangeFinder') as mock_exchange_finder, \
             patch('exchange_rates.lib.converter.async_populate_all') as mock_populate:
            mock_instance = mock_exchange_finder.return_value
            mock_instance.get_currency_rates_list.return_value = {
                self.today: {'USD': 1.0}
            }

            result = converter(source_currency='USD', value=100)

            expected = {
                "date": self.today,
                "source_currency": {"USD": 100},
                "exchanged_currency": {}
            }
            self.assertEqual(result, expected)
            mock_populate.assert_called_once()