from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms import layout as cfl
from crispy_forms.helper import FormHelper
from .models import User


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'initials', 'birth_date', 'email',)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.action = ''
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
                    """
<a href="javascript:history.back()" class="btn btn-secondary mr-3">Zurück</a>
                    """),
                cfl.Submit(
                    'submit',
                    'Registrieren',
                    css_class='btn btn-primary'
                ),
            ),
        )
