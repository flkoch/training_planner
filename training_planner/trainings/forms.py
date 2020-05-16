from django import forms as forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from crispy_forms import layout as cfl
from crispy_forms.helper import FormHelper
from tempus_dominus import widgets
import members.models as members
from .models import Training


class AddTrainingForm(forms.ModelForm):
    main_instructor = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        empty_label=_('Trainer wählen'), label=_('Haupttrainer'))
    instructor = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        required=False, label=_('Assistenztrainer'))
    start = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': 'DD.MM.YYYY HH:mm',
                'sideBySide': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
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
        self.fields['instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        for field in ['description', 'location', 'instructor']:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            'title',
            'description',
            cfl.Row(
                cfl.Field(
                    'start',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'duration',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'location',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'capacity',
                    wrapper_class='col-auto',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'main_instructor',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                ),
                cfl.Field(
                    'instructor',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.Field(
                    'target_group',
                    wrapper_class='col-auto',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.HTML(
                    _(
                        '''
                        <p class="col-auto my-4 text-muted">
                        Bitte &langle;<strong>Ctrl</strong>&rangle; gedrückt
                        halten, um die Auswahl zu ändern</p>
                        '''
                    )
                ),
            ),
            cfl.Row(
                cfl.HTML(
                    '''
                        <a href="javascript:history.back()"
                        class="btn btn-secondary mr-3">%(back)s</a>
                    ''' % {
                        'back': _('Zurück')
                    }
                ),
                cfl.Submit(
                    'submit',
                    _('Training erstellen'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class TrainingForm(forms.ModelForm):
    main_instructor = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        empty_label=_('Trainer wählen'), label=_('Haupttrainer'))
    instructor = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        required=False, label=_('Assistenztrainer'))
    registration_open = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': 'DD.MM.YYYY HH:mm',
                'sideBySide': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
    )
    registration_close = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': 'DD.MM.YYYY HH:mm',
                'sideBySide': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
    )
    start = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': 'DD.MM.YYYY HH:mm',
                'sideBySide': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
    )

    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['deleted', 'archived']

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['main_instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['coordinator'].queryset = \
            members.participant().order_by('first_name', 'last_name')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        for field in ['description', 'location', 'instructor', 'coordinator',
                      'registered_participants', 'participants']:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            'title',
            'description',
            cfl.Row(
                cfl.Field(
                    'start',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'duration',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'location',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'capacity',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'coordinator',
                    wrapper_class='col-auto',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'main_instructor',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                ),
                cfl.Field(
                    'instructor',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.Field(
                    'target_group',
                    wrapper_class='col-auto',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.HTML(
                    _(
                        '''
                        <p class="col-auto my-4 text-muted">
                        Bitte &langle;<strong>Ctrl</strong>&rangle; gedrückt
                        halten, um die Auswahl zu ändern</p>
                        '''
                    )
                ),
            ),
            cfl.Row(
                cfl.HTML(
                    '''
                        <a href="javascript:history.back()"
                        class="btn btn-secondary mr-3">%(back)s</a>
                    ''' % {
                        'back': _('Zurück')
                    }
                ),
                cfl.Submit(
                    'submit',
                    _('Speichern'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class AdminTrainingForm(forms.ModelForm):
    registration_open = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': 'DD.MM.YYYY HH:mm',
                'sideBySide': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
    )
    registration_close = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': 'DD.MM.YYYY HH:mm',
                'sideBySide': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
    )
    start = forms.DateTimeField(
        widget=widgets.DateTimePicker(
            options={
                'stepping': 15,
                'format': 'DD.MM.YYYY HH:mm',
                'sideBySide': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
    )

    class Meta:
        model = Training
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['main_instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['instructor'].queryset = \
            members.trainer().order_by('first_name', 'last_name')
        self.fields['registered_participants'].queryset = \
            members.participant().order_by('first_name', 'last_name')
        self.fields['participants'].queryset = \
            members.participant().order_by('first_name', 'last_name')
        self.fields['coordinator'].queryset = \
            members.participant().order_by('first_name', 'last_name')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        self.helper.html5_required = True
        for field in ['description', 'location', 'instructor', 'coordinator',
                      'registered_participants', 'participants', 'archived',
                      'deleted']:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            'title',
            'description',
            cfl.Row(
                cfl.Field(
                    'start',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'duration',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'location',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'capacity',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'coordinator',
                    wrapper_class='col-auto',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'main_instructor',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                ),
                cfl.Field(
                    'instructor',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.Field(
                    'target_group',
                    wrapper_class='col-auto',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.HTML(
                    _(
                        '''
                        <p class="col-auto my-4 text-muted">
                        Bitte &langle;<strong>Ctrl</strong>&rangle; gedrückt
                        halten, um die Auswahl zu ändern</p>
                        '''
                    )
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'registered_participants',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.Field(
                    'participants',
                    wrapper_class='col-12 col-sm-5 col-md-4 col-lg-3',
                    help_text=_('Bitte <Ctrl> gedrückt halten, '
                                'um Auswahl zu ändern.'),
                ),
                cfl.HTML(
                    _(
                        '''
                        <p class="col-auto my-4 text-muted">
                        Bitte &langle;<strong>Ctrl</strong>&rangle; gedrückt
                        halten, um die Auswahl zu ändern</p>
                        '''
                    )
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'registration_open',
                    wrapper_class='col-auto',
                ),
                cfl.Field(
                    'registration_close',
                    wrapper_class='col-auto',
                ),
            ),
            cfl.Row(
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
                    '''
                        <a href="javascript:history.back()"
                        class="btn btn-secondary mr-3">%(back)s</a>
                    ''' % {
                        'back': _('Zurück')
                    }
                ),
                cfl.Submit(
                    'submit',
                    _('Speichern'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class TrainingSeriesForm(forms.ModelForm):
    dates = forms.DateField(
        widget=widgets.DatePicker(
            options={
                'format': 'DD.MM.YYYY',
                'sideBySide': True,
                'useCurrent': False,
                'allowMultidate': True
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        label=_('Daten')
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
        for field in ['description', 'location', 'instructor', 'coordinator',
                      'registered_participants', 'participants']:
            self.fields[field].required = False
        self.helper.layout = cfl.Layout(
            cfl.HTML(
                _(
                    '''
                    <p class="my-3">Weitere Trainings zu {{training}} vom
                    {{training.start}} erstellen.<br />
                    Bitte die Daten der Trainings auswählen.</p>
                    '''
                )
            ),
            'dates',
            cfl.Row(
                cfl.HTML(
                    '''
                        <a href="javascript:history.back()"
                        class="btn btn-secondary mr-3">%(back)s</a>
                    ''' % {
                        'back': _('Zurück')
                    }
                ),
                cfl.Submit(
                    'submit',
                    _('Speichern'),
                    css_class='btn btn-primary'
                ),
            ),
        )
