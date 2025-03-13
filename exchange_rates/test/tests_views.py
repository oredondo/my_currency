from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from currencies.models import Currency
from providers.models import Credentials
from exchange_rates.models import CurrencyExchangeRate


class ExchangeRateListViewTests(APITestCase):
    def setUp(self):
        # Set up client and authenticated user
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')  # SessionAuthentication
        self.usd = Currency.objects.create(code='USD', name='US Dollar')
        self.eur = Currency.objects.create(code='EUR', name='Euro')
        self.gbp = Currency.objects.create(code='GBP', name='British Pound')
        self.provider = Credentials.objects.create(name='Mock', token='random',
                                                   url='www.url.com', enabled=True, priority=1)

        # URL for ExchangeRateListView
        self.url = reverse('v1:concurrency_rate_list')  # Matches name='concurrency_rate_list'

    def tearDown(self):
        # Clean up after tests
        self.client.logout()
        User.objects.all().delete()

    def test_unauthenticated_access_denied(self):
        # Test that an unauthenticated user cannot access the view
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_query_params(self):
        # Test that missing query parameters return 400 Bad Request
        response = self.client.get(self.url)  # No params provided
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_exchange_rate_list(self):
        # Test successful retrieval of exchange rates with valid params
        params = {
            "source_currency": "USD",
            "date_from": "2025-01-01",
            "date_to": "2025-01-01"
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("2025-01-01")), 2)


class ConverterViewTests(APITestCase):
    def setUp(self):
        # Set up client and authenticated user
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.usd = Currency.objects.create(code='USD', name='US Dollar')
        self.eur = Currency.objects.create(code='EUR', name='Euro')
        self.gbp = Currency.objects.create(code='GBP', name='British Pound')
        self.provider = Credentials.objects.create(name='Mock', token='random',
                                                   url='www.url.com', enabled=True, priority=1)

        # URL for ConverterView
        self.url = reverse('v1:convert_amount')  # Matches name='convert_amount'

    def tearDown(self):
        # Clean up after tests
        self.client.logout()
        User.objects.all().delete()
        Currency.objects.all().delete()
        CurrencyExchangeRate.objects.all().delete()

    def test_unauthenticated_access_denied(self):
        # Test that an unauthenticated user cannot access the view
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_query_params(self):
        # Test that missing query parameters return 400 Bad Request
        response = self.client.get(self.url)  # No params provided
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_amount_type(self):
        # Test that an invalid (non-integer) amount returns 400 Bad Request
        params = {
            "source_currency": "USD",
            "exchanged_currency": "EUR",
            "amount": "invalid"  # Not an integer
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('exchange_rates.views.converter')  # Mock converter function
    def test_successful_conversion_single_currency(self, mock_converter):
        # Test successful currency conversion with a single target currency
        mock_converter.return_value = {"converted_amount": {"EUR": 93.0}}

        params = {
            "source_currency": "USD",
            "exchanged_currency": "EUR",
            "amount": "100"
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"converted_amount": {"EUR": 93.0}})
        mock_converter.assert_called_once_with(
            source_currency="USD", exchanged_currency=["EUR"], value=100
        )

    @patch('exchange_rates.views.converter')
    def test_successful_conversion_multiple_currencies(self, mock_converter):
        # Test successful conversion with multiple target currencies (comma-separated)
        mock_converter.return_value = {"converted_amount": {"EUR": 93.0, "GBP": 80.0}}

        params = {
            "source_currency": "USD",
            "exchanged_currency": "EUR,GBP",
            "amount": "100"
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"converted_amount": {"EUR": 93.0, "GBP": 80.0}})
        mock_converter.assert_called_once_with(
            source_currency="USD", exchanged_currency=["EUR", "GBP"], value=100
        )

    @patch('exchange_rates.views.converter')
    def test_converter_exception(self, mock_converter):
        # Test that an exception in converter returns 400 Bad Request
        mock_converter.side_effect = Exception("Conversion error")
        params = {
            "source_currency": "USD",
            "exchanged_currency": "EUR",
            "amount": "100"
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
