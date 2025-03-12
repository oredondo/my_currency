from django import forms

from currencies.models import Currency


class ConverterForm(forms.Form):
    """
        A Django form for collecting currency conversion input from the user.

        Fields:
            source_currency (ModelChoiceField): A dropdown to select the source currency.
            exchanged_currency (ModelMultipleChoiceField): A checkbox list to select one or more target currencies.
            amount (IntegerField): An input field for the amount to convert.
    """

    source_currency = forms.ModelChoiceField(queryset=Currency.objects.all(),
                                             label="Code of currency", required=True)
    exchanged_currency = forms.ModelMultipleChoiceField(queryset=Currency.objects.all(),
                                                        label="Code of exchanged_currency",
                                                        widget=forms.widgets.CheckboxSelectMultiple(),
                                                        required=True)
    amount = forms.IntegerField(label="Amount to exchange", required=True)
