# Generated by Django 3.1 on 2023-02-24 04:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20230224_0704'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='driver',
            options={'ordering': ['added']},
        ),
    ]
