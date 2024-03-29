from collections.abc import Iterable

from crispy_forms import layout as cfl
from crispy_forms.helper import FormHelper
from django import forms as forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from tempus_dominus import widgets

import members.models as members

from .models import Location, TargetGroup, Training


def _python2moment(date_time_string):
    """
    Transforms a python datetime string into a valid moment.js datetime string
    by replacing the corresponding placeholders.
    """
    if isinstance(date_time_string, str):
        return date_time_string.replace('%Y', 'YYYY').replace('%m', 'MM')\
            .replace('%d', 'DD').replace('%H', 'HH').replace('%M', 'mm')\
            .replace('%a', 'ddd').replace('%A', 'dddd').replace('%w', 'e')\
            .replace('%b', 'MMM').replace('%B', 'MMMM').replace('%y', 'YY')\
            .replace('%I', 'hh').replace('%p', 'a').replace('%f', 'ssssss')\
            .replace('%S', 'ss').replace('%z', 'ZZ').replace('%j', 'DDDD')\
            .replace('%U', 'WW').replace('%W', 'ww').replace('%%', '%')
    elif isinstance(date_time_string, Iterable):
        return [_python2moment(item) for item in date_time_string]
    else:
        raise ValueError('Expecting string or iterable of strings.')
        return None


def _moment2python(date_time_string):
    """
    Transforms a momentum.js datetime string into a valid python datetime
    string by replacing the corresponding placeholders.
    """
    if isinstance(date_time_string, str):
        return date_time_string.replace('YYYY', '%Y').replace('MM', '%m')\
            .replace('DD', '%d').replace('HH', '%H').replace('mm', '%M')\
            .replace('ddd', '%a').replace('dddd', '%A').replace('e', '%w')\
            .replace('MMM', '%b').replace('MMMM', '%B').replace('YY', '%y')\
            .replace('hh', '%I').replace('a', '%p').replace('ssssss', '%f')\
            .replace('ss', '%S').replace('ZZ', '%z').replace('DDDD', '%j')\
            .replace('WW', '%U').replace('ww', '%W').replace('%', '%%')
    elif isinstance(date_time_string, Iterable):
        return [_moment2python(item) for item in date_time_string]
    else:
        raise ValueError('Expecting string or iterable of strings.')
        return None


class AddTrainingForm(forms.ModelForm):
    main_instructor = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        empty_label=_('Choose main instructor'), label=_('Main instructor'))
    instructors = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        required=False, label=_('Instructor'))
    start = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': _python2moment(
                    settings.DATETIME_INPUT_FORMATS[2]
                ),
                'sideBySide': True,
                'extraFormats': _python2moment(
                    settings.DATETIME_INPUT_FORMATS
                ),
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            },
        ),
        label=_('Start'),
    )

    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['deleted', 'archived', 'registration_open',
                   'registration_close', 'coordinator',
                   'registered_participants', 'participants']

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['main_instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['instructors'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['location'].queryset = \
            Location.objects.all().order_by('name')
        self.fields['target_group'].queryset = \
            TargetGroup.objects.all().order_by('name')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        for field in ['description', 'location', 'instructors']:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Field(
                    'title',
                    wrapper_class='col-12 col-sm-6 col-md-8 col-lg-9'
                ),
                cfl.Field(
                    'main_instructor',
                    wrapper_class='col-12 col-sm-6 col-md-4 col-lg-3',
                ),
            ),
            'description',
            cfl.Row(
                cfl.Field(
                    'start',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'duration',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'location',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'capacity',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'instructors',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.Field(
                    'target_group',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.Field(
                    'restrictions',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.HTML(
                    _(
                        '<p class="col-auto my-4 text-muted">'
                        'Please hold down &langle;<strong>Ctrl</strong>'
                        '&rangle; to change the selection.</p>'
                    )
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'enable_registration',
                    wrapper_class='col-12 col-sm-4',
                ),
                cfl.Field(
                    'enable_coordinator',
                    wrapper_class='col-12 col-sm-4',
                ),
                cfl.Field(
                    'enable_visitors',
                    wrapper_class='col-12 col-sm-4',
                ),
            ),
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" '
                        'class="btn btn-secondary mr-3">{back}</a>',
                        back=_('Back')
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Create Training'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class TrainingForm(forms.ModelForm):
    main_instructor = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        empty_label=_('Choose main instructor'), label=_('Main instructor'))
    instructors = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        required=False, label=_('Instructor'))
    start = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': _python2moment(settings.DATETIME_INPUT_FORMATS[2]),
                'sideBySide': True,
                'extraFormats': _python2moment(
                    settings.DATETIME_INPUT_FORMATS
                ),

            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        label=_('Start'),
    )

    class Meta:
        model = Training
        exclude = [
            'participants',
            'deleted',
            'archived',
            'registration_open',
            'registration_close',
        ]

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['main_instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['instructors'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['registered_participants'].queryset = \
            members.participant().order_by('first_name', 'last_name')
        self.fields['visitors'].queryset = \
            members.all().order_by('first_name', 'last_name')
        self.fields['coordinator'].queryset = \
            members.all().order_by('first_name', 'last_name')
        self.fields['location'].queryset = \
            Location.objects.all().order_by('name')
        self.fields['target_group'].queryset = \
            TargetGroup.objects.all().order_by('name')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        for field in ['description', 'location', 'instructors', 'coordinator',
                      'registered_participants', 'visitors', ]:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Field(
                    'title',
                    wrapper_class='col-12 col-sm-6 col-md-8 col-lg-9'
                ),
                cfl.Field(
                    'main_instructor',
                    wrapper_class='col-12 col-sm-6 col-md-4 col-lg-3',
                ),
            ),
            'description',
            cfl.Row(
                cfl.Field(
                    'start',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'duration',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'location',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'capacity',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'instructors',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.Field(
                    'target_group',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.Field(
                    'restrictions',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.HTML(
                    _(
                        '<p class="col-auto my-4 text-muted">'
                        'Please hold down &langle;<strong>Ctrl</strong>'
                        '&rangle; to change the selection.</p>'
                    )
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'registered_participants',
                    wrapper_class='col-12 col-md-6',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'
                    ),
                ),
                cfl.Field(
                    'visitors',
                    wrapper_class='col-12  col-md-6',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'
                    ),
                ),
                cfl.HTML(
                    _(
                        '<p class="col-auto my-4 text-muted">'
                        'Please hold down &langle;<strong>Ctrl</strong>'
                        '&rangle; to change the selection.</p>'
                    )
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'enable_registration',
                    wrapper_class='col-12 col-sm-4',
                ),
                cfl.Field(
                    'enable_coordinator',
                    wrapper_class='col-12 col-sm-4',
                ),
                cfl.Field(
                    'enable_visitors',
                    wrapper_class='col-12 col-sm-4',
                ),
            ),
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" '
                        'class="btn btn-secondary mr-3">{back}</a>',
                        back=_('Back')
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Save'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class AdminTrainingForm(forms.ModelForm):
    registration_open = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': _python2moment(settings.DATETIME_INPUT_FORMATS[2]),
                'sideBySide': True,
                'extraFormats': _python2moment(
                    settings.DATETIME_INPUT_FORMATS
                ),
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        label=_('Registration opening'),
    )
    registration_close = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': _python2moment(settings.DATETIME_INPUT_FORMATS[2]),
                'sideBySide': True,
                'extraFormats': _python2moment(
                    settings.DATETIME_INPUT_FORMATS
                ),
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        label=_('Registration closing'),
    )
    start = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': _python2moment(settings.DATETIME_INPUT_FORMATS[2]),
                'sideBySide': True,
                'extraFormats': _python2moment(
                    settings.DATETIME_INPUT_FORMATS
                ),
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        label=_('Start'),
    )

    class Meta:
        model = Training
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['main_instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['instructors'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['registered_participants'].queryset = \
            members.participant().order_by('first_name', 'last_name')
        self.fields['participants'].queryset = \
            members.participant().order_by('first_name', 'last_name')
        self.fields['visitors'].queryset = \
            members.all().order_by('first_name', 'last_name')
        self.fields['coordinator'].queryset = \
            members.all().order_by('first_name', 'last_name')
        self.fields['location'].queryset = \
            Location.objects.all().order_by('name')
        self.fields['target_group'].queryset = \
            TargetGroup.objects.all().order_by('name')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        for field in ['description', 'location', 'instructors', 'coordinator',
                      'registered_participants', 'participants', 'archived',
                      'deleted', 'visitors', ]:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Field(
                    'title',
                    wrapper_class='col-12 col-sm-6 col-md-8 col-lg-9'
                ),
                cfl.Field(
                    'main_instructor',
                    wrapper_class='col-12 col-sm-6 col-md-4 col-lg-3',
                ),
            ),
            'description',
            cfl.Row(
                cfl.Field(
                    'start',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'duration',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'location',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
                cfl.Field(
                    'capacity',
                    wrapper_class='col-12 col-sm-6 col-md-3',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'instructors',
                    wrapper_class='col-12 col-sm-6 col-md-4 col-lg-3',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.Field(
                    'target_group',
                    wrapper_class='col-12 col-sm-6 col-md-4 col-lg-3',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.Field(
                    'restrictions',
                    wrapper_class='col-12 col-sm-6 col-md-4 col-lg-3',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'),
                ),
                cfl.Field(
                    'coordinator',
                    wrapper_class='col-12 col-sm-6 col-md-4 col-lg-3',
                ),
                cfl.HTML(
                    _(
                        '<p class="col-auto my-4 text-muted">'
                        'Please hold down &langle;<strong>Ctrl</strong>'
                        '&rangle; to change the selection.</p>'
                    )
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'registered_participants',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'
                    ),
                ),
                cfl.Field(
                    'participants',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'
                    ),
                ),
                cfl.Field(
                    'visitors',
                    wrapper_class='col-12 col-sm-6 col-md-4',
                    help_text=_(
                        'Please hold down <Ctrl> to change the selection.'
                    ),
                ),
                cfl.HTML(
                    _(
                        '<p class="col-auto my-4 text-muted">'
                        'Please hold down &langle;<strong>Ctrl</strong>'
                        '&rangle; to change the selection.</p>'
                    )
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'registration_open',
                    wrapper_class='col-6',
                ),
                cfl.Field(
                    'registration_close',
                    wrapper_class='col-6',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'enable_registration',
                    wrapper_class='col-12 col-sm-4',
                ),
                cfl.Field(
                    'enable_coordinator',
                    wrapper_class='col-12 col-sm-4',
                ),
                cfl.Field(
                    'enable_visitors',
                    wrapper_class='col-12 col-sm-4',
                ),
                cfl.Field(
                    'archived',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'deleted',
                    wrapper_class='col-auto',
                ),
            ),
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" '
                        'class="btn btn-secondary mr-3">{back}</a>',
                        back=_('Back')
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Save'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class TrainingSeriesForm(forms.ModelForm):
    dates = forms.DateField(
        widget=widgets.DatePicker(
            options={
                'format': _python2moment(settings.DATE_INPUT_FORMAT[0]),
                'useCurrent': False,
                'allowMultidate': True,
                'extraFormats': _python2moment(settings.DATE_INPUT_FORMATS),
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        label=_('Dates')
    )

    class Meta:
        model = Training
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        for field in ['description', 'location', 'instructors', 'coordinator',
                      'registered_participants', 'participants']:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            cfl.HTML(
                _(
                    '<p class="my-3">Create further trainings like '
                    '{{training.name}} starting at {{training.start}}.<br>'
                    'Please select the dates below. To not select todays '
                    'date, finish your selection, reopen the widget and '
                    'deselect today.</p>'
                )
            ),
            'dates',
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" '
                        'class="btn btn-secondary mr-3">{back}</a>',
                        back=_('Back')
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Save'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class TrainingArchiveDays(forms.Form):
    days = forms.IntegerField(
        label=_('Days:'),
        initial=0,
    )
    weeks = forms.IntegerField(
        label=_('Weeks:'),
        initial=12,
    )
    checked = forms.BooleanField(
        label=_('only checked'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'id': 'days_checked',
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        self.helper.form_id = 'TrainingArchiveDays'
        self.helper.layout = cfl.Layout(
            cfl.Row(
                'days',
                'weeks',
                'checked',
            ),
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" '
                        'class="btn btn-secondary mr-3">{back}</a>',
                        back=_('Back')
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Archive'),
                    css_class='btn btn-primary',
                ),
            ),
        )


class TrainingArchiveDate(forms.Form):
    date = forms.DateField(
        widget=widgets.DatePicker(
            options={
                'format': _python2moment(settings.DATE_INPUT_FORMAT[0]),
                'useCurrent': False,
                'extraFormats': _python2moment(settings.DATE_INPUT_FORMATS),
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': 'true',
            },
        ),
        label=_('Archive trainings starting before:')
    )
    checked = forms.BooleanField(
        label=_('only checked'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'id': 'date_checked',
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.form_id = 'TrainingArchiveDate'
        self.helper.html5_required = True
        self.helper.layout = cfl.Layout(
            cfl.Row(
                'date',
                'checked',
            ),
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" '
                        'class="btn btn-secondary mr-3">{back}</a>',
                        back=_('Back')
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Archive'),
                    css_class='btn btn-primary',
                ),
            ),
        )
