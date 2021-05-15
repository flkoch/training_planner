import dateparser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

# Create your models here.


def _list_items_as_string(*args):
    """
    Helper function returning a list of strings from *args.
    """
    return [str(item) for item in args if item is not None]


class Address(models.Model):
    """
    Class to store a regular address
    composed of fields for street, house number, area code, city and country
    string representation gives comma separated concatenation
    """
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
        ordering = ['country', 'city', 'street', 'house_number']

    def __str__(self):
        """
        return string of comma separated concatenation of fields
        """
        line = ', '.join([
            ' '.join(_list_items_as_string(self.street, self.house_number)),
            ' '.join(_list_items_as_string(self.area_code, self.city)),
            self.country
        ])
        return line


class Location(models.Model):
    """
    Class to store a location as combination of a name, description, an
    instance of the previous address class and a capacity for that location.
    """
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
        ordering = ['name', '-capacity']

    def __str__(self):
        """
        return string representation as name
        """
        return self.name

    @property
    def with_address(self):
        """
        return string representation including the address, separedt by comma
        """
        return ', '.join(_list_items_as_string(self, self.address))


class TargetGroup(models.Model):
    """
    Class for storing target goups as combination of name and description.
    """
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    description = models.TextField(
        verbose_name=_('Description'), max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = _('Target Group')
        verbose_name_plural = _('Target Groups')
        ordering = ['name']

    def __str__(self):
        """
        return string representation as name
        """
        return self.name


class Training(models.Model):
    """
    Class for storing trainings. The following fields exist:
    title                   str             title of training
    description             str             description of training (content)
    start                   datetime        start of training
    duration                int             duration in minutes
    location                Location        location of training
    main_instructor         User            main instructor for training
    instructors             Users           further instructors
    coordinator             User            coordinator for training
    target_group            target_groups   target groups for training
    capacity                int             capacity of training
    registered_participants Users   people registered to take part
    participants            Users           people actually taking part
    deleted                 bool            flag to mark as deleted
    archived                bool            flag to mark as archived
    registration_open       datetime        earliest possible registration time
    registration_close      datetime        latest possible registration time
    enable_registration     boolean         flag to enable registration for
                                            participants
    enable_visitors         boolean         flag to enable registration for
                                            visitors
    enable_coordinator      boolean         flag to enable registration for
                                            coordinator
    """
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
    instructors = models.ManyToManyField(
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
    visitors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='visited_trainings', blank=True,
        default=None, verbose_name=_('Visitors')
    )
    deleted = models.BooleanField(verbose_name=_('Deleted'), default=False)
    archived = models.BooleanField(verbose_name=_('Archived'), default=False)
    registration_open = models.DateTimeField(
        verbose_name=_('Registration opening'), default=timezone.now)
    registration_close = models.DateTimeField(
        verbose_name=_('Registration closing'))
    enable_registration = models.BooleanField(
        verbose_name=_('Allow registration'),
        default=True
    )
    enable_visitors = models.BooleanField(
        verbose_name=_('Allow visitors'),
        default=True
    )
    enable_coordinator = models.BooleanField(
        verbose_name=_('Use coordinator'),
        default=True
    )

    class Meta:
        verbose_name = _('Training')
        verbose_name_plural = _('Trainings')
        ordering = ['-start', 'duration', 'title']

    def __str__(self):
        """
        return string as name and date of session
        """
        return f'{self.name} ({self.startdate_as_text})'

    def get_absolute_url(self):
        return reverse('trainings-details', kwargs={'id': self.id})

    @property
    def name(self):
        """
        return string as name consisting of shorthand identifier consisting of
        weekday, time and main instructor
        """
        identifier = ''.join([self.weekday_as_text.upper()[:2],
                              timezone.localtime(self.start).strftime('%H%M'),
                              self.main_instructor
                              .get_initials_paranthesised()])
        return f'{identifier}: {self.title}'

    @property
    def weekday_as_text(self):
        """
        return locale aware weekday of start as string
        """
        return date_format(timezone.localtime(self.start), 'l')

    @property
    def starttime_as_text(self):
        """
        return locale aware start time as string
        """
        return date_format(
            timezone.localtime(self.start),
            format='TIME_FORMAT',
            use_l10n=True,
        )

    @property
    def opentime_as_text(self):
        """
        return locale aware registration opeining time as string
        """
        return date_format(
            timezone.localtime(self.registration_open),
            format='TIME_FORMAT',
            use_l10n=True,
        )

    @property
    def closetime_as_text(self):
        """
        return locale aware registration close time as string
        """
        return date_format(
            timezone.localtime(self.registration_close),
            format='TIME_FORMAT',
            use_l10n=True,
        )

    @property
    def startdate_as_text(self):
        """
        return locale aware start date as string
        """
        return date_format(
            timezone.localtime(self.start),
            format='DATE_FORMAT',
            use_l10n=True,
        )

    @property
    def opendate_as_text(self):
        """
        return locale aware registration open date as string
        """
        return date_format(
            timezone.localtime(self.registration_open),
            format='DATE_FORMAT',
            use_l10n=True,
        )

    @property
    def closedate_as_text(self):
        """
        return locale aware registration close date as string
        """
        return date_format(
            timezone.localtime(self.registration_close),
            format='DATE_FORMAT',
            use_l10n=True,
        )

    @property
    def target_groups_as_text(self):
        """
        return list of target groups
        """
        return [group.name for group in self.target_group.all()]

    @property
    def free_capacity(self):
        """
        return free capacity as difference between capacity and current
        registrations
        """
        return self.capacity - self.registered_participants.all().count()

    @property
    def before_registration(self):
        """
        return True if we are currently before the registration period,
        false otherwise
        """
        return timezone.now() < self.registration_open

    @property
    def during_registration(self):
        """
        return True if we are currently within the registration period,
        false otherwise
        """
        return self.registration_open <= timezone.now() \
            <= self.registration_close

    @property
    def after_registration(self):
        """
        returns True if the registration period is over, false otherwise
        """
        return self.registration_close < timezone.now() <= self.start

    def can_register(self, user=None):
        """
        Returns True if the user can currently register as participant or if
        a user can currently register if no user id is supplied, false
        otherwise.
        A user can register if the training is neither archived nor deleted,
        the registration period is open and the user is neither instructor nor
        the main instructor for that training.
        """
        if not self.enable_registration:
            return False
        if self.deleted or self.archived:
            return False
        if isinstance(user, get_user_model()):
            if self.is_instructor(user) or \
                not user.groups.filter(name='Participant') \
                    .exists():
                return False
        return self.during_registration and \
            self.registered_participants.all().count() < self.capacity

    def can_unregister(self, user):
        """
        Returns True if the user can currently unregister as participant,
        false otherwise.
        A user can unregister if the user currently is registered and the
        registration period is open.
        """
        if not self.enable_registration:
            return False
        if self.deleted or self.archived:
            return False
        return self.during_registration and self.is_registered(user)

    def can_register_visitor(self, user=None):
        """
        Returns True if the user can currently register as visitor or if
        a user can currently register if no user id is supplied, false
        otherwise.
        A user can register if the training is neither archived nor deleted,
        the registration period is open and the user is neither instructor nor
        the main instructor for that training.
        """
        if not self.enable_visitors:
            return False
        if self.deleted or self.archived:
            return False
        if isinstance(user, get_user_model()):
            if self.is_instructor(user) or \
                    self.is_registered(user):
                return False
        return self.during_registration

    def can_unregister_visitor(self, user):
        """
        Returns True if the user can currently unregister as visitor,
        false otherwise.
        A user can unregister if the user currently is registered and the
        registration period is open.
        """
        if not self.enable_visitors:
            return False
        if self.deleted or self.archived:
            return False
        return self.during_registration and self.is_visitor(user)

    def is_registered(self, user):
        """
        returns True if the user is currently registered as participant,
        false otherwise
        """
        return user in self.registered_participants.all()

    def is_visitor(self, user):
        """
        returns True if the user is currently registered as visitor,
        false otherwise
        """
        return user in self.visitors.all()

    def is_instructor(self, user):
        """
        returns True if the user is either main instructor or instructor,
        false otherwise
        """
        return user == self.main_instructor or user in self.instructors.all()

    def can_edit(self, user):
        """
        Returns True if the user can edit the training, false otherwise.
        A user can edit a training if the user is a member of the
        administrator group or is either main instructor or instructor for the
        training. Only administrators can edit deleted and archived trainings.
        """
        if user.groups.filter(name='Administrator').exists():
            return True
        if self.deleted or self.archived:
            return False
        return self.is_instructor(user)

    def register_participant(self, user):
        """
        Register the user for the training session as participant and return
        a boolean indicating whether the registration was successful. Note
        that the registration is also successfull, if the user is already
        registered. However, the user will only be listed once as registered
        participant.
        """
        if self.can_register(user):
            if self.is_visitor(user):
                self.visitors.remove(user)
            self.registered_participants.add(user)
            return True
        else:
            return False

    def unregister_participant(self, user):
        """
        Remove the user from the registered participants for the training
        session. Return a bolean indicating whether the sign off was
        successful, as for example the registration period could be over or
        the user was not registered as participant in the first place.
        """
        if self.can_unregister(user):
            self.registered_participants.remove(user)
            return True
        else:
            return False

    def register_visitor(self, user):
        """
        Register the user for the training session as visitor and return
        a boolean indicating whether the registration was successful. Note
        that the registration is also successfull, if the user is already
        registered as visitor. However, the user will only be listed once as
        visitor.
        """
        if self.can_register_visitor(user):
            self.visitors.add(user)
            return True
        else:
            return False

    def unregister_visitor(self, user):
        """
        Remove the user from the visitors for the training  session. Return a
        bolean indicating whether the sign off was successful, as for example
        the registration period could be over or the user was not registered
        as visitor in the first place.
        """
        if self.can_unregister_visitor(user):
            self.visitors.remove(user)
            return True
        else:
            return False

    def register_coordinator(self, user):
        """
        Register user as coordinator, if that is possible. There can only be a
        single coordinator (return value 1 if someone is already coordinator).
        The main instructor may not be coordinator (return value 2). If the
        user is successfully registered as coordinator the return value is 3.
        """
        if not self.enable_coordinator:
            return 3
        if self.coordinator is not None:
            return 1
        elif user == self.main_instructor:
            return 2
        else:
            self.coordinator = user
            self.save()
            return 0

    def unregister_coordinator(self):
        """
        Reset the coordinator field to None, deleting whoever was coordinator
        before.
        """
        self.coordinator = None
        self.save()
        return True

    def set_registration_times(
        self,
        start_day=14,
        start_hour=0,
        end_day=0,
        end_hour=-2,
    ):
        """
        Set self.registration_open to self.start - start_days - start_hours and
        self.registration_close to self.start - end_days - end_hours.
        """
        self.registration_open = self.start - timezone.timedelta(
            days=start_day,
            hours=start_hour,
        )
        self.registration_close = self.start - timezone.timedelta(
            days=end_day,
            hours=end_hour,
        )
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
