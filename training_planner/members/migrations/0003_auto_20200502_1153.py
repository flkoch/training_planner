# Generated by Django 3.0.5 on 2020-05-02 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20200502_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='initials',
            field=models.CharField(blank=True, max_length=3, null=True, verbose_name='Initialen'),
        ),
    ]
