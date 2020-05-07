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
        if self.initials is None:
            if self.first_name == self.last_name == '':
                return self.username[:2].upper()
            return (self.first_name[0] + self.last_name[0]).upper()
        return self.initials

    def get_initials_paranthesised(self):
        return self.get_initials().join(['(', ')'])

    def get_public_name(self):
        if self.first_name:
            lastnames = self.last_name.split()
            lastname = ''
            for name in lastnames:
                lastname += name[0] + '. '
            return self.first_name + ' ' + lastname[:-1]
        return self.username

    @property
    def name(self):
        return ' '.join([self.first_name, self.last_name])

    @property
    def name_or_username(self):
        if self.first_name:
            return ' '.join([self.first_name, self.last_name])
        return self.username

    @property
    def is_trainer(self):
        return self.groups.filter(name='Trainer').exists()

    @property
    def is_active_trainer(self):
        return self.groups.filter(name='Active Trainer').exists()

    @property
    def is_participant(self):
        return self.groups.filter(name='Participant').exists()

    @property
    def is_active_participant(self):
        return self.groups.filter(name='Active Participant').exists()


def active_trainer():
    return User.objects.filter(groups__name='Active Trainer')


def trainer():
    return User.objects.filter(groups__name='Trainer')
