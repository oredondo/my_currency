from rest_framework import viewsets

from .models import Currency
from .serializers import CurrencySerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class CurrencyViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
