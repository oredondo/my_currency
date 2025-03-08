# Generated by Django 5.1.7 on 2025-03-07 15:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('concurrencies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valuation_date', models.DateField(db_index=True)),
                ('rate_value', models.DecimalField(db_index=True, decimal_places=6, max_digits=18)),
                ('exchanged_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concurrencies.currency')),
                ('source_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges', to='concurrencies.currency')),
            ],
        ),
    ]
