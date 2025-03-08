from unittest.mock import Mock, patch
from concurrencies.models import Currency
import requests
from django.test import TestCase

from .adapters.currency_beacon import CurrencyBeaconAdapter


class CurrencyBeaconAdapterTestCase(TestCase):
    def setUp(self):
        """Set up the test case with a CurrencyBeaconAdapter instance."""
        self.token = "test_token"
        self.url = "https://api.currencybeacon.com"
        self.adapter = CurrencyBeaconAdapter(token=self.token, url=self.url)

    @patch('providers.adapters.currency_beacon.requests.get')
    def test_get_exchange_rate_data_success(self, mock_get):
        """Test successful retrieval of exchange rate data."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {
                "EUR": 0.85
            }
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.adapter.get_exchange_rate_data(
            source_currency="USD",
            exchanged_currency="EUR",
            valuation_date="2023-01-01"
        )

        # Assertions
        self.assertEqual(result, 0.85)
        mock_get.assert_called_once_with(
            "https://api.currencybeacon.com/v1/historical?base=USD&date=2023-01-01&symbols=EUR",
            headers={"Authorization": "Bearer test_token"}
        )

    @patch('providers.adapters.currency_beacon.requests.get')
    def test_get_exchange_rate_data_api_error(self, mock_get):
        """Test handling of API request failure."""
        # Mock an API error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(requests.exceptions.HTTPError):
            self.adapter.get_exchange_rate_data(
                source_currency="USD",
                exchanged_currency="EUR",
                valuation_date="2023-01-01"
            )

    @patch('concurrencies.models.Currency.objects.filter')
    @patch('providers.adapters.currency_beacon.requests.get')
    def test_get_timeseries_rates_success(self, mock_get, mock_currency_filter):
        """Test successful retrieval of timeseries rates."""
        # Mock the Currency model query
        mock_currency_filter.return_value.values_list.return_value = ["EUR"]

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "2023-01-01": {"EUR": 0.85},
                "2023-01-02": {"EUR": 0.86},
                "2023-01-03": {"EUR": 0.87}
            }
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.adapter.get_timeseries_rates(
            source_currency="USD",
            start_date="2023-01-01",
            end_date="2023-01-03"
        )

        # Assertions
        expected = {
                "2023-01-01": {"EUR": 0.85},
                "2023-01-02": {"EUR": 0.86},
                "2023-01-03": {"EUR": 0.87}
            }
        self.assertEqual(result, expected)
        mock_get.assert_called_once_with(
            "https://api.currencybeacon.com/v1/timeseries?base=USD&"
            "symbols=EUR&start_date=2023-01-01&start_date=2023-01-03",
            headers={"Authorization": "Bearer test_token"}
        )
        mock_currency_filter.assert_called_once_with(code__iexact="USD")

    def test_get_timeseries_rates_invalid_date_format(self):
        """Test handling of invalid date format."""
        with self.assertRaises(ValueError) as context:
            self.adapter.get_timeseries_rates(
                source_currency="USD",
                start_date="2023-13-01",  # Invalid month
                end_date="2023-01-03"
            )
        self.assertIn("Dates must be in YYYY-MM-DD format", str(context.exception))

    def test_get_timeseries_rates_start_after_end(self):
        """Test handling of start date after end date."""
        with self.assertRaises(ValueError) as context:
            self.adapter.get_timeseries_rates(
                source_currency="USD",
                start_date="2023-01-03",
                end_date="2023-01-01"
            )
        self.assertIn("start_date must be earlier than end_date", str(context.exception))

    @patch('concurrencies.models.Currency.objects.filter')
    @patch('providers.adapters.currency_beacon.requests.get')
    def test_get_timeseries_rates_api_error(self, mock_get, mock_currency_filter):
        """Test handling of API request failure in timeseries."""
        # Mock the Currency model query
        mock_currency_filter.return_value.values_list.return_value = ["EUR"]

        # Mock an API error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception) as context:
            self.adapter.get_timeseries_rates(
                source_currency="USD",
                start_date="2023-01-01",
                end_date="2023-01-03"
            )
        self.assertIn("Failed to retrieve exchange rates from API", str(context.exception))

    @patch('concurrencies.models.Currency.objects.filter')
    @patch('providers.adapters.currency_beacon.requests.get')
    def test_get_timeseries_rates_invalid_response(self, mock_get, mock_currency_filter):
        """Test handling of invalid API response format in timeseries."""
        # Mock the Currency model query
        mock_currency_filter.return_value.values_list.return_value = ["EUR"]

        # Mock an invalid response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"wrong_key": "no_rates_here"}
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception) as context:
            self.adapter.get_timeseries_rates(
                source_currency="USD",
                start_date="2023-01-01",
                end_date="2023-01-03"
            )
        self.assertIn("Invalid response format from API", str(context.exception))

    @patch('concurrencies.models.Currency.objects.filter')
    def test_get_timeseries_rates_currency_not_found(self, mock_currency_filter):
        """Test handling of non-existent currency code."""
        # Mock the Currency model query to raise DoesNotExist
        mock_currency_filter.return_value.values_list.side_effect = Currency.DoesNotExist

        # Call the method and expect an exception
        with self.assertRaises(ValueError) as context:
            self.adapter.get_timeseries_rates(
                source_currency="XXX",  # Non-existent currency
                start_date="2023-01-01",
                end_date="2023-01-03"
            )
        self.assertIn("Currency codes does not exist, you need to add", str(context.exception))

