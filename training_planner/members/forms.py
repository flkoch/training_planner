from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'initials', 'birth_date', )
