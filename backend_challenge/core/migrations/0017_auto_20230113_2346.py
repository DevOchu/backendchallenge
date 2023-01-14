# Generated by Django 3.1 on 2023-01-13 23:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_routesettings_vehicle_capacity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='routesettings',
            old_name='vehicle_utilization',
            new_name='vehicle_selection',
        ),
        migrations.RemoveField(
            model_name='routesettings',
            name='num_vehicles',
        ),
    ]
