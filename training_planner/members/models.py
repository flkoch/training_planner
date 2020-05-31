from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import datetime


def _participant():
    return _('Participant')


def _active_participant():
    return _('Active Participant')


def _trainer():
    return _('Trainer')


def _active_trainer():
    return _('Active Trainer')


def _administrator():
    return _('Administrator')


class User(AbstractUser):
    birth_date = models.DateField(
        verbose_name=_('Date of Birth'), null=True, blank=True)
    initials = models.CharField(
        max_length=3, verbose_name=_('Initials'), null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        full_name = self.get_full_name()
        if not full_name.strip():
            return f"{self.username}"
        else:
            return full_name

    def get_initials(self):
        if self.initials is None or (isinstance(self.initials, str) and
                                     not self.initials.strip()):
            if self.first_name.strip() and self.last_name.strip():
                return (self.first_name[0] + self.last_name[0]).upper()
            elif len(self.username) < 3:
                return self.usernamen.upper()
            else:
                return self.username[:2].upper()
        return self.initials

    def get_initials_paranthesised(self):
        return self.get_initials().join(['(', ')'])

    def get_public_name(self):
        if self.first_name.strip():
            lastnames = self.last_name.split()
            lastname = ''
            for name in lastnames:
                lastname += name[0] + '. '
            return self.first_name + ' ' + lastname[:-1]
        return self.username

    def get_groups_locale(self):
        group_names = {
            'Participant': _participant,
            'Active Participant': _active_participant,
            'Trainer': _trainer,
            'Active Trainer': _active_trainer,
            'Administrator': _administrator,
        }
        groups_locale = [func() for func in [group_names.get(str(group), None)
                                             for group in self.groups.all()]
                         if func is not None]
        return groups_locale

    @property
    def name(self):
        return self.get_full_name()

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
        return self.groups.filter(name='Active Participant') \
            .exists()

    @property
    def is_administrator(self):
        return self.groups.filter(name='Administrator').exists()


def active_participant():
    return User.objects.filter(
        groups__name='Active Participant'
    ).exclude(groups__name='System')


def participant():
    return User.objects.filter(groups__name='Participant') \
        .exclude(groups__name='System')


def active_trainer():
    return User.objects.filter(groups__name='Active Trainer') \
        .exclude(groups__name='System')


def trainer():
    return User.objects.filter(groups__name='Trainer') \
        .exclude(groups__name='System')


def check_active_participants(**kwargs):
    users = participant()
    group = Group.objects.get(name='Active Participant')
    active_users = users.filter(
        trainings__start__gte=timezone.now() - datetime.timedelta(**kwargs)
    )
    group.user_set.remove(
        *users.difference(active_users).values_list('id', flat=True)
    )
    group.user_set.add(*active_users.values_list('id', flat=True))


def check_active_trainers(**kwargs):
    trainers = trainer()
    group = Group.objects.get(name='Active Trainer')
    time = timezone.now() - datetime.timedelta(**kwargs)
    active_instructors = trainers.filter(instructor__start__gte=time)
    active_assistants = trainers.filter(assistant__start__gte=time)
    print(active_instructors)
    print(active_assistants)
    group.user_set.remove(*trainers.difference(
        active_instructors, active_assistants).values_list('id', flat=True)
    )
    group.user_set.add(*active_instructors.union(
        active_assistants).values_list('id', flat=True))


def check_trainers(**kwargs):
    time = timezone.now() - datetime.timedelta(**kwargs)
    instructors = User.objects.filter(instructor__start__gte=time)
    assistants = User.objects.filter(assistant__start__gte=time)
    group = Group.objects.get(name='Trainer')
    group.user_set.add(
        *instructors.union(assistants).values_list('id', flat=True)
    )
