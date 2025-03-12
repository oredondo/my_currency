# Create your views here.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .lib.converter import converter
from .lib.exchange_finder import ExchangeFinder



class ExchangeRateListView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        source = request.query_params.get("source_currency")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if source is None or date_from is None or date_to is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            exchange = ExchangeFinder(source_currency=source, start_date=date_from, end_date=date_to)
            out = exchange.get_currency_rates_list()
        except Exception as e:
            # return Response(status=status.HTTP_400_BAD_REQUEST)
            raise e

        return Response(out)


class ConverterView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
