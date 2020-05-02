from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Address(models.Model):
    street = models.CharField(max_length=150, verbose_name="Strasse")
    house_number = models.CharField(
        max_length=10, verbose_name="Hausnummer", blank=True, null=True)
    area_code = models.CharField(
        max_length=15, verbose_name="Potsleitzahl", blank=True, null=True)
    city = models.CharField(max_length=180, verbose_name="Stadt")
    country = models.CharField(
        max_length=100, verbose_name="Land", blank=True, null=True)

    def __str__(self):
        line = f"{self.street} {self.house_number}, {self.area_code} " \
            f"{self.city}, {self.country}"
        return line


class Location(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name")
    description = models.TextField(
        verbose_name="Beschreibung", blank=True, null=True)
    address = models.ForeignKey(
        Address, blank=True, null=True, on_delete=models.SET_NULL)
    capacity = models.PositiveSmallIntegerField(
        verbose_name="Kapazität (Anzahl Personen)", blank=True, null=True)

    def __str__(self):
        return self.name


class TargetGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name")
    description = models.TextField(
        verbose_name="Beschreibung", max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name


class Training(models.Model):
    title = models.CharField(max_length=100, verbose_name="Bezeichnung")
    description = models.TextField(verbose_name="Beschreibung", blank=True)
    start = models.DateTimeField(verbose_name="Start")
    duration = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(240)],
        verbose_name="Dauer (min)")
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True)
    main_instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="main_instructor")
    instructor = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="further_instructors",
        default=None, blank=True)
    target_group = models.ManyToManyField(
        TargetGroup, verbose_name="Zielgruppe")

    def __str__(self):
        starttime = ''.join([self.start.strftime('%a').upper()[:2],
                             self.start.strftime('%H%M'),
                             self.main_instructor
                             .get_initials_paranthesised()])
        return f"{starttime}: {self.title}"
