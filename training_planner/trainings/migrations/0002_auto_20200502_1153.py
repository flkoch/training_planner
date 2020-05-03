# Generated by Django 3.0.5 on 2020-05-02 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='description',
            field=models.TextField(blank=True, verbose_name='Beschreibung'),
        ),
        migrations.AlterField(
            model_name='training',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Bezeichnung'),
        ),
    ]