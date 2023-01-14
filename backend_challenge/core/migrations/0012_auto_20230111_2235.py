# Generated by Django 3.1 on 2023-01-11 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_routesettings_num_vehicles'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='availability_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='status',
            field=models.CharField(choices=[('draft', 'draft'), ('pending', 'pending'), ('delivered', 'delivered'), ('assigned', 'assigned')], default='pending', max_length=20),
        ),
    ]
