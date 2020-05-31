from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
import dateparser

# Create your models here.


def _list_items_as_string(*args):
    return [str(item) for item in args if item is not None]


class Address(models.Model):
    street = models.CharField(max_length=150, verbose_name=_('Street'))
    house_number = models.CharField(
        max_length=10, verbose_name=_('House number'), blank=True, null=True)
    area_code = models.CharField(
        max_length=15, verbose_name=_('Postal code'), blank=True, null=True)
    city = models.CharField(max_length=180, verbose_name=_('City'))
    country = models.CharField(
        max_length=100, verbose_name=_('Country'), blank=True, null=True)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        line = ', '.join([
            ' '.join(_list_items_as_string(self.street, self.house_number)),
            ' '.join(_list_items_as_string(self.area_code, self.city)),
            self.country
        ])
        return line


class Location(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    description = models.TextField(
        verbose_name=_('Description'), blank=True, null=True)
    address = models.ForeignKey(
        Address, blank=True, null=True, on_delete=models.CASCADE)
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_('Capacity (number of people)'), blank=True, null=True)

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')

    def __str__(self):
        return self.name

    @property
    def with_address(self):
        return ', '.join(_list_items_as_string(self, self.address))


class TargetGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    description = models.TextField(
        verbose_name=_('Description'), max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = _('Target Group')
        verbose_name_plural = _('Target Groups')

    def __str__(self):
        return self.name


class Training(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'), blank=True)
    start = models.DateTimeField(verbose_name=_('Start'))
    duration = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(240)],
        verbose_name=_('Duration (min.)'))
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, related_name='trainings',
        verbose_name=_('Location'), blank=True, null=True)
    main_instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='instructor', verbose_name=_('Main Instructor'))
    instructor = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='assistant',
        default=None, blank=True, verbose_name=_('Instructor'))
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.PROTECT,
                                    related_name='coordinated_trainings',
                                    verbose_name=_('Coordinator'),
                                    null=True, blank=True, default=None)
    target_group = models.ManyToManyField(
        TargetGroup, verbose_name=_('Target Group'))
    capacity = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1), MaxValueValidator(50)],
        verbose_name=_('Capacity (number of people)'), default=15)
    registered_participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='trainings_registered',
        blank=True, default=None, verbose_name=_('Registered Participants'))
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='trainings', blank=True,
        default=None, verbose_name=_('Participants'))
    deleted = models.BooleanField(verbose_name=_('Deleted'), default=False)
    archived = models.BooleanField(verbose_name=_('Archived'), default=False)
    registration_open = models.DateTimeField(
        verbose_name=_('Registration opening'), default=timezone.now)
    registration_close = models.DateTimeField(
        verbose_name=_('Registration closing'))

    class Meta:
        verbose_name = _('Training')
        verbose_name_plural = _('Trainings')

    def __str__(self):
        starttime = ''.join([self.weekday_as_text.upper()[:2],
                             timezone.localtime(self.start).strftime('%H%M'),
                             self.main_instructor
                             .get_initials_paranthesised()])
        return f'{starttime}: {self.title}'

    @property
    def weekday_as_text(self):
        return date_format(self.start, 'l')

    @property
    def starttime_as_text(self):
        return date_format(
            timezone.localtime(self.start),
            format='TIME_FORMAT',
            use_l10n=True,
        )

    @property
    def opentime_as_text(self):
        return date_format(
            timezone.localtime(self.registration_open),
            format='TIME_FORMAT',
            use_l10n=True,
        )

    @property
    def closetime_as_text(self):
        return date_format(
            timezone.localtime(self.registration_close),
            format='TIME_FORMAT',
            use_l10n=True,
        )

    @property
    def startdate_as_text(self):
        return date_format(
            timezone.localtime(self.start),
            format='DATE_FORMAT',
            use_l10n=True,
        )

    @property
    def opendate_as_text(self):
        return date_format(
            timezone.localtime(self.registration_open),
            format='DATE_FORMAT',
            use_l10n=True,
        )

    @property
    def closedate_as_text(self):
        return date_format(
            timezone.localtime(self.registration_close),
            format='DATE_FORMAT',
            use_l10n=True,
        )

    @property
    def target_groups_as_text(self):
        return [_(group.name) for group in self.target_group.all()]

    @property
    def free_capacity(self):
        return self.capacity - self.registered_participants.all().count()

    @property
    def before_registration(self):
        return timezone.now() < self.registration_open

    @property
    def during_registration(self):
        return self.registration_open <= timezone.now() \
            <= self.registration_close

    @property
    def after_registration(self):
        return self.registration_close < timezone.now() <= self.start

    def can_register(self, user=None):
        if isinstance(user, get_user_model()):
            if self.is_instructor(user) or \
                not user.groups.filter(name='Participant') \
                    .exists():
                return False
        return self.during_registration and \
            self.registered_participants.all().count() < self.capacity

    def can_unregister(self, user):
        return self.registration_open <= timezone.now() \
            <= self.registration_close and self.is_registered(user)

    def is_registered(self, user):
        return user in self.registered_participants.all()

    def is_instructor(self, user):
        return user == self.main_instructor or user in self.instructor.all()

    def can_edit(self, user):
        return self.is_instructor(user) or \
            user.groups.filter(name='Administrator').exists()

    def register(self, user):
        if self.can_register(user):
            self.registered_participants.add(user)
            return True
        else:
            return False

    def unregister(self, user):
        if self.is_registered(user):
            self.registered_participants.remove(user)
        return True

    def register_as_coordinator(self, user):
        if self.coordinator is not None:
            return 1
        elif user == self.main_instructor:
            return 2
        else:
            self.coordinator = user
            self.save()
            return 0

    def unregister_coordinator(self):
        self.coordinator = None
        self.save()
        return True

    def set_registration_times(self, start=14, end=2):
        """
        Set self.registration_open to self.start - start days and
        self.registration_close to self.start - end days.
        """
        self.registration_open = self.start - timezone.timedelta(days=start)
        self.registration_close = self.start - timezone.timedelta(days=end)
        return self


def archive_trainings(days=0, weeks=0, date=None, checked=True):
    """
    Set all trainings to archived, if they started more than the added time
    before now. The checked parameter determines to whether to only archive
    items where all the registered participants have been confirmed.
    """
    if date is not None:
        trainings = Training.objects.filter(
            start__lte=timezone.make_aware(
                dateparser.parse(date, locales=['de', 'en']))
        ).filter(
            archived=False
        )
    else:
        trainings = Training.objects.filter(
            start__lte=timezone.now() - timezone.timedelta(
                days=days, weeks=weeks)
        ).filter(
            archived=False
        )
    if checked:
        for training in trainings:
            if (set(training.participants.all()) ==
                    set(training.registered_participants.all())):
                training.archived = True
    else:
        for training in trainings:
            training.archived = True
    Training.objects.bulk_update(trainings, ['archived'])
