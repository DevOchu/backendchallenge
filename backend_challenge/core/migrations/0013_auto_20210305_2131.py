# Generated by Django 3.1.1 on 2021-03-05 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20210305_1951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='added',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='edited',
        ),
    ]
