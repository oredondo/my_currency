from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.db.models.signals import post_save
from currencies.signals import post_save_currency
from currencies.models import Currency


class CurrencyViewSetTests(APITestCase):
    def setUp(self):
        # Set up client and authenticated user
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        post_save.disconnect(post_save_currency, sender=Currency)

        self.currency1 = Currency.objects.create(code='USD', name='US Dollar')
        self.currency2 = Currency.objects.create(code='EUR', name='Euro')

        self.list_url = reverse('currency-list')
        self.detail_url = reverse('currency-detail', kwargs={'code': 'USD'})

    def test_unauthenticated_access_denied(self):
        # Test that an unauthenticated user cannot access the list
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_currencies_authenticated(self):
        # Test that an authenticated user can list currencies
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return the 2 created currencies

    def test_retrieve_currency_authenticated(self):
        # Test that an authenticated user can retrieve a specific currency
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'USD')
        self.assertEqual(response.data['name'], 'US Dollar')

    def test_create_currency_authenticated(self):
        # Test that an authenticated user can create a currency
        data = {'code': 'GBP', 'name': 'Libra', 'symbol': 'BP'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Currency.objects.count(), 3)  # Now there are 3 currencies
        self.assertEqual(Currency.objects.get(code='GBP').name, 'Libra')

    def test_update_currency_authenticated(self):
        # Test that an authenticated user can update a currency
        data = {'code': 'USD', 'name': 'Dollar', 'symbol': '$'}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.currency1.refresh_from_db()
        self.assertEqual(self.currency1.name, 'Dollar')

    def test_delete_currency_authenticated(self):
        # Test that an authenticated user can delete a currency
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Currency.objects.count(), 1)  # Only 1 currency remains
        self.assertFalse(Currency.objects.filter(code='USD').exists())

    def test_retrieve_nonexistent_currency(self):
        # Test that attempting to retrieve a nonexistent currency returns 404
        nonexistent_url = reverse('currency-detail', kwargs={'code': 'XXX'})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        post_save.connect(post_save_currency, sender=Currency)
        # Clean up after tests
        self.client.logout()
        Currency.objects.all().delete()
        User.objects.all().delete()
