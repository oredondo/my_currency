from django import forms

from currencies.models import Currency


class ConverterForm(forms.Form):
    source_currency = forms.ModelChoiceField(queryset=Currency.objects.all(),
                                             label="Code of currency", required=True)
    exchanged_currency = forms.ModelMultipleChoiceField(queryset=Currency.objects.all(),
                                                        label="Code of exchanged_currency",
                                                        widget=forms.widgets.CheckboxSelectMultiple(),
                                                        required=True)
    amount = forms.IntegerField(label="Amount to exchange", required=True)
