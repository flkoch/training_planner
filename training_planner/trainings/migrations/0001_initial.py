# Generated by Django 3.0.5 on 2020-05-05 14:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=150, verbose_name='Strasse')),
                ('house_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Hausnummer')),
                ('area_code', models.CharField(blank=True, max_length=15, null=True, verbose_name='Potsleitzahl')),
                ('city', models.CharField(max_length=180, verbose_name='Stadt')),
                ('country', models.CharField(blank=True, max_length=100, null=True, verbose_name='Land')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Beschreibung')),
                ('capacity', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Kapazität (Anzahl Personen)')),
                ('address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trainings.Address')),
            ],
        ),
        migrations.CreateModel(
            name='TargetGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('description', models.TextField(blank=True, max_length=500, null=True, verbose_name='Beschreibung')),
            ],
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Bezeichnung')),
                ('description', models.TextField(blank=True, verbose_name='Beschreibung')),
                ('start', models.DateTimeField(verbose_name='Start')),
                ('duration', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(240)], verbose_name='Dauer (min)')),
                ('capacity', models.PositiveSmallIntegerField(default=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)], verbose_name='Kapazität (Anzahl Teilnehmer)')),
                ('deleted', models.BooleanField(default=False, verbose_name='Gelöscht')),
                ('archived', models.BooleanField(default=False, verbose_name='Archiviert')),
                ('registration_open', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Anmeldebeginn')),
                ('registration_close', models.DateTimeField(verbose_name='Anmeldeschluss')),
                ('coordinator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='coordinated_trainins', to=settings.AUTH_USER_MODEL, verbose_name='Trainingskoordinator')),
                ('instructor', models.ManyToManyField(blank=True, default=None, related_name='assistant', to=settings.AUTH_USER_MODEL, verbose_name='Assistenztrainer')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='trainings.Location')),
                ('main_instructor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instructor', to=settings.AUTH_USER_MODEL, verbose_name='Haupttrainer')),
                ('participants', models.ManyToManyField(blank=True, default=None, related_name='trainings', to=settings.AUTH_USER_MODEL)),
                ('registered_participants', models.ManyToManyField(blank=True, default=None, related_name='trainings_registered', to=settings.AUTH_USER_MODEL)),
                ('target_group', models.ManyToManyField(to='trainings.TargetGroup', verbose_name='Zielgruppe')),
            ],
        ),
    ]
