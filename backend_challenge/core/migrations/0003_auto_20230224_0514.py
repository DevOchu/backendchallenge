# Generated by Django 3.1 on 2023-02-24 02:14

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20230224_0458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='delivery_adress',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(36.7866471, -1.2981014), srid=4326),
        ),
    ]
