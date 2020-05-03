# Generated by Django 3.0.5 on 2020-05-02 18:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainings', '0003_auto_20200502_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='capacity',
            field=models.PositiveSmallIntegerField(default=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)], verbose_name='Kapazität (Anzahl Teilnehmer)'),
        ),
        migrations.AlterField(
            model_name='targetgroup',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Beschreibung'),
        ),
    ]