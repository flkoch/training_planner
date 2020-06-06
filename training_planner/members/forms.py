from crispy_forms import layout as cfl
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from tempus_dominus import widgets

from .models import User


class CreateUserForm(UserCreationForm):
    birth_date = forms.DateField(
        widget=widgets.DatePicker(
            options={
                'format': 'DD.MM.YYYY',
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        required=False,
        label=_('Date of Birth'),
    )
    initials = forms.CharField(
        required=False,
        label=_('Initials'),
        max_length=3,
        min_length=2,
    )

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'initials', 'birth_date', 'email',)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        for field in ['first_name', 'last_name', 'email']:
            self.fields[field].required = True
        self.helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Field(
                    'first_name',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
                cfl.Field(
                    'last_name',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'initials',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
                cfl.Field(
                    'birth_date',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'username',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
                cfl.Field(
                    'email',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'password1',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
                cfl.Field(
                    'password2',
                    wrapper_class='col-12 col-md-6 col-xl-4',
                ),
            ),
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" class="btn '
                        'btn-secondary mr-3">{back}</a>',
                        back=_('Back'),
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Register'),
                    css_class='btn btn-primary'
                ),
            ),
        )


class ChangeUserForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=widgets.DatePicker(
            options={
                'format': 'DD.MM.YYYY',
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        required=False,
        label=_('Date of Birth'),
    )
    initials = forms.CharField(
        required=False,
        label=_('Initials'),
        max_length=3,
        min_length=2,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'birth_date', 'initials', 'email',)

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
        for field in ['first_name', 'last_name', 'email']:
            self.fields[field].required = True
        self.helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Field(
                    'first_name',
                    wrapper_class='col-12 col-sm-6 col-xl-4',
                ),
                cfl.Field(
                    'last_name',
                    wrapper_class='col-12 col-sm-4 col-lg-5 col-xl-4',
                ),
                cfl.Field(
                    'initials',
                    wrapper_class='col-12 col-sm-2 col-lg-1',
                ),
            ),
            cfl.Row(
                cfl.Field(
                    'birth_date',
                    wrapper_class='col-12 col-sm-6 col-xl-4',
                ),
                cfl.Field(
                    'email',
                    wrapper_class='col-12 col-sm-6 col-xl-5',
                ),
            ),
            cfl.Row(
                cfl.HTML(
                    format_lazy(
                        '<a href="javascript:history.back()" class="btn '
                        'btn-secondary mr-3">{back}</a>',
                        back=_('Back'),
                    )
                ),
                cfl.Submit(
                    'submit',
                    _('Save'),
                    css_class='btn btn-primary'
                ),
            ),
        )
