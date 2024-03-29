# Generated by Django 3.2 on 2021-04-24 10:33

from django.contrib.auth.models import Group
from django.db import migrations


def forward_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).get_or_create(name='System')
    Group.objects.using(db_alias).get_or_create(name='Administrator')
    Group.objects.using(db_alias).get_or_create(name='Trainer')
    Group.objects.using(db_alias).get_or_create(name='Active Trainer')
    Group.objects.using(db_alias).get_or_create(name='Participant')
    Group.objects.using(db_alias).get_or_create(name='Active Participant')


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20201026_1830'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
