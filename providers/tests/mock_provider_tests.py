import random
from datetime import datetime, date

from django.test import TestCase

from providers.adapters.mock_provider import MockProvider

# Set random seed for reproducible tests
random.seed(42)


class TestMockProvider(TestCase):
    def setUp(self):
        """Set up method that runs before each test, creating a fresh MockProvider instance."""
        self.provider = MockProvider(token="test_token", url="https://test-api.com", )

    def test_init(self):
        """Test to verify correct initialization of MockProvider."""
        self.assertEqual(self.provider.token, "test_token")
        self.assertEqual(self.provider.url, "https://test-api.com")

    def test_date_range(self):
        """Test to verify the _date_range method generates correct date sequences."""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 3)

        dates, start = self.provider._date_range(start_date, end_date)

        # Check that the date list has the expected length
        self.assertEqual(len(dates), 3)
        # Verify each date in the sequence
        self.assertEqual(dates[0], date(2023, 1, 1))
        self.assertEqual(dates[1], date(2023, 1, 2))
        self.assertEqual(dates[2], date(2023, 1, 3))
        # Verify the returned start date
        self.assertEqual(start, date(2023, 1, 1))

    def test_generate_random_rate(self):
        """Test to verify that generate_random_rate produces reasonable values."""
        base_rate = 1.0
        rate = self.provider.generate_random_rate(base_rate)

        # Check that the rate is within the expected range (±5%)
        self.assertTrue(0.95 <= rate <= 1.05)
        # Verify the rate is a float
        self.assertIsInstance(rate, float)
        # Check that the rate is rounded to 4 decimal places
        self.assertEqual(round(rate, 4), rate)

    def test_get_timeseries_rates(self):
        """Test to verify get_timeseries_rates returns correctly formatted data."""
        # Use patch to mock pre_get_timeseries
        with self.settings():
            with self.subTest("Mocking pre_get_timeseries"):
                from unittest.mock import patch
                with patch('your_app.models.pre_get_timeseries') as mock_pre_get:
                    # Mock return value for pre_get_timeseries
                    mock_pre_get.return_value = (datetime(2023, 1, 1),
                                                 datetime(2023, 1, 2),
                                                 "USD,EUR")

                    result = self.provider.get_timeseries_rates(
                        source_currency="GBP",
                        start_date=datetime(2023, 1, 1),
                        end_date=datetime(2023, 1, 2)
                    )

                    # Verify result is a dictionary
                    self.assertIsInstance(result, dict)
                    # Check the number of days in the result
                    self.assertEqual(len(result), 2)
                    # Verify expected dates are present
                    self.assertIn("2023-01-01", result)
                    self.assertIn("2023-01-02", result)

                    # Check that each date has the expected currencies and valid rates
                    for date_str in result:
                        self.assertIn("USD", result[date_str])
                        self.assertIn("EUR", result[date_str])
                        self.assertTrue(0.95 <= result[date_str]["USD"] <= 1.05)
                        self.assertTrue(0.95 <= result[date_str]["EUR"] <= 1.05)

    def test_get_timeseries_rates_single_day(self):
        """Test to verify get_timeseries_rates works correctly for a single day."""
        with self.settings():
            from unittest.mock import patch
            with patch('providers.adapters.mock_provider.pre_get_timeseries') as mock_pre_get:
                # Mock return value for a single-day range
                mock_pre_get.return_value = (datetime(2023, 1, 1),
                                             datetime(2023, 1, 1),
                                             "USD")

                result = self.provider.get_timeseries_rates(
                    source_currency="GBP",
                    start_date=datetime(2023, 1, 1),
                    end_date=datetime(2023, 1, 1)
                )

                # Verify result contains exactly one day
                self.assertEqual(len(result), 1)
                # Check the expected date is present
                self.assertIn("2023-01-01", result)
                # Verify the currency is included with a valid rate
                self.assertIn("USD", result["2023-01-01"])
                self.assertTrue(0.95 <= result["2023-01-01"]["USD"] <= 1.05)
