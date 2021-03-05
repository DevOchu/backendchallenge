# Generated by Django 3.1.1 on 2021-03-05 21:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20210305_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
