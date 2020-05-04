from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    birth_date = models.DateField(
        verbose_name="Geburtsdatum", null=True, blank=True)
    is_trainer = models.BooleanField(default=False, verbose_name="Trainer")
    active_trainer = models.BooleanField(
        default=False, verbose_name="aktiver Trainer")
    active_participant = models.BooleanField(
        default=True, verbose_name="aktiver Teilnehmer")
    initials = models.CharField(
        max_length=3, verbose_name="Initialen", null=True, blank=True)

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}"
        if full_name.isspace():
            return f"{self.username}"
        else:
            return full_name

    def get_initials(self):
        return self.initials

    def get_initials_paranthesised(self):
        return self.initials.join(['(', ')'])


def trainer():
    return User.objects.filter(active_trainer=True)
