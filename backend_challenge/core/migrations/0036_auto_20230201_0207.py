# Generated by Django 3.1 on 2023-01-31 23:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20230201_0133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='trip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trip_deliveries', to='core.trip'),
        ),
    ]
