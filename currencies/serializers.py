from rest_framework import serializers

from .models import Currency


class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Currency
        lookup_field = 'code'
        fields = ['code', 'name', 'symbol']
