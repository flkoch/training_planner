# Generated by Django 3.2 on 2021-04-24 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trainings', '0007_auto_20201026_1830'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['country', 'city', 'street', 'house_number'], 'verbose_name': 'Address', 'verbose_name_plural': 'Addresses'},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['name', '-capacity'], 'verbose_name': 'Location', 'verbose_name_plural': 'Locations'},
        ),
        migrations.AlterModelOptions(
            name='targetgroup',
            options={'ordering': ['name'], 'verbose_name': 'Target Group', 'verbose_name_plural': 'Target Groups'},
        ),
        migrations.AlterModelOptions(
            name='training',
            options={'ordering': ['-start', 'duration', 'title'], 'verbose_name': 'Training', 'verbose_name_plural': 'Trainings'},
        ),
    ]
