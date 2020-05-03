# Generated by Django 3.0.5 on 2020-05-02 20:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trainings', '0004_auto_20200502_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='registered_participants',
            field=models.ManyToManyField(blank=True, default=None, related_name='trainings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='training',
            name='instructor',
            field=models.ManyToManyField(blank=True, default=None, related_name='assistant', to=settings.AUTH_USER_MODEL, verbose_name='Assistenztrainer'),
        ),
        migrations.AlterField(
            model_name='training',
            name='main_instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instructor', to=settings.AUTH_USER_MODEL, verbose_name='Haupttrainer'),
        ),
    ]