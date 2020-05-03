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

    @property
    def with_address(self):
        return ', '.join([str(self), str(self.address)])


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
        related_name="instructor", verbose_name="Haupttrainer")
    instructor = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="assistant",
        default=None, blank=True, verbose_name="Assistenztrainer")
    target_group = models.ManyToManyField(
        TargetGroup, verbose_name="Zielgruppe")
    capacity = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Kapazität (Anzahl Teilnehmer)", default=15)
    registered_participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="trainings",
        blank=True, default=None)

    def __str__(self):
        starttime = ''.join([self.weekday_as_text.upper()[:2],
                             self.start.strftime('%H%M'),
                             self.main_instructor
                             .get_initials_paranthesised()])
        return f"{starttime}: {self.title}"

    @property
    def weekday_as_text(self):
        return self.start.strftime('%A')

    @property
    def starttime_as_text(self):
        return self.start.strftime('%H:%M')

    @property
    def target_groups_as_text(self):
        return [group.name for group in self.target_group.all()]

    @property
    def free_capacity(self):
        return self.capacity - self.registered_participants.all().count()
