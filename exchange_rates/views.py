from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from providers.adapters.create_provider import CreateProvider

class ExchangeRateListView(APIView):
    def get(self, request):
        source = request.query_params.get("source_currency")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        create = CreateProvider()
        provider = create.create()
        # Lógica para obtener tasas
        try:
            out = provider.get_exchange_rate_data(source_currency=source, exchanged_currency=)
        except Exception:
            raise Exception

        return Response({"rates": []})