from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    birth_date = models.DateField(
        verbose_name="Geburtsdatum", null=True, blank=True)
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

    @property
    def is_trainer(self):
        return True

    @property
    def is_active_trainer(self):
        return True

    @property
    def is_active_participant(self):
        return True


def trainer():
    return User.objects.filter(groups__name='active_trainer')
