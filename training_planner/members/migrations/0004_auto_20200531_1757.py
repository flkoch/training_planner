# Generated by Django 3.0.5 on 2020-05-31 15:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_auto_20200528_1445'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['last_name', 'first_name'], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
