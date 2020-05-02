# Generated by Django 3.0.5 on 2020-05-02 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Geburtsdatum'),
        ),
        migrations.AlterField(
            model_name='user',
            name='initials',
            field=models.TextField(blank=True, max_length=3, null=True, verbose_name='Initialen'),
        ),
    ]
