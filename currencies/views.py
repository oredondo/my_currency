from rest_framework import viewsets

from .models import Currency
from .serializers import CurrencySerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class CurrencyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Currency instances.

    Provides endpoints for listing, retrieving, creating, updating, and deleting
    Currency objects, with authentication and permission enforcement.

    retrieve:
    Currency instance info

    list:
    Return a list of all the Currency instances.

    create:
    Create a new Currency instance.

    update:
    Update information in Currency.

    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
