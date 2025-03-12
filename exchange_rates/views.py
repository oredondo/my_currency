# Create your views here.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .libs.converter import converter
from .libs.exchange_finder import ExchangeFinder



class ExchangeRateListView(APIView):
    """
    API view to retrieve a list of exchange rates for a source currency over a date range.

    get_params:

        source_currency (str): The currency code of the source currency (e.g., 'USD').
        date_from (str): The start date in 'YYYY-MM-DD' format.
        date_to (str): The end date in 'YYYY-MM-DD' format.

    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to fetch exchange rates for a specified source currency and date range.

        Args:
            request (Request): The HTTP request object containing query parameters.

        Query Parameters:
            source_currency (str): The currency code of the source currency (e.g., 'USD').
            date_from (str): The start date in 'YYYY-MM-DD' format.
            date_to (str): The end date in 'YYYY-MM-DD' format.

        Returns:
            Response: A JSON response containing:
                - Success: A dictionary of exchange rates if all parameters are valid and data is retrieved.
                - Error: HTTP 400 status if parameters are missing or invalid, or if an exception occurs.

        Raises:
            Exception: Propagates any unhandled exceptions from ExchangeFinder for debugging purposes.
        """
        source = request.query_params.get("source_currency")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if source is None or date_from is None or date_to is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            exchange = ExchangeFinder(source_currency=source, start_date=date_from, end_date=date_to)
            out = exchange.get_currency_rates_list()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            # raise e

        return Response(out)


class ConverterView(APIView):
    """
    API view to convert an amount from a source currency to one or more target currencies.

    get_params:
        source_currency (str): The currency code of the source currency (e.g., 'USD').
        exchanged_currency (str): A comma-separated list of target currency codes (e.g., 'EUR,GBP').
        amount (str): The amount to convert, expected to be an integer.
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to convert an amount between currencies.

        Args:
            request (Request): The HTTP request object containing query parameters.

        Query Parameters:
            source_currency (str): The currency code of the source currency (e.g., 'USD').
            exchanged_currency (str): A comma-separated list of target currency codes (e.g., 'EUR,GBP').
            amount (str): The amount to convert, expected to be an integer.

        Returns:
            Response: A JSON response containing:
                - Success: A dictionary with conversion results if all parameters are valid.
                - Error: HTTP 400 status if parameters are missing, invalid, or if conversion fails.
        """
        try:
            source = request.query_params.get("source_currency")
            exchanged_currency = request.query_params.get("exchanged_currency")
            value = int(request.query_params.get("amount"))
        except (ValueError, TypeError):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if source is None or exchanged_currency is None or value is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            out = converter(source_currency=source,
                            exchanged_currency=exchanged_currency.split(','), value=value)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(out)
