from django.forms import ModelForm, ModelChoiceField, ModelMultipleChoiceField
from django.contrib.auth import get_user_model
from .models import Training


class AddTrainingForm(ModelForm):
    main_instructor = ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        empty_label="Trainer wählen")
    instructor = ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Trainer'),
        required=False)

    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['deleted', 'archived', 'registration_open',
                   'registration_close', 'coordinator',
                   'registered_participants', 'participants']


class TrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['deleted', 'archived']


class AdminTrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
