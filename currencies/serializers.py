from rest_framework import serializers

from .models import Currency


class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Currency model.

    Converts Currency model instances to JSON representations and vice versa,
    including hyperlinks to related resources. Used for API endpoints.
    """
    class Meta:
        model = Currency
        lookup_field = 'code'
        fields = ['code', 'name', 'symbol']
