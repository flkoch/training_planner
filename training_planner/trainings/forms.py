from django.forms import ModelForm
from .models import Training


class AddTrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = ['title', 'description', 'start', 'duration', 'location',
                  'main_instructor', 'instructor', 'target_group', 'capacity']


class TrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['deleted', 'archived']


class AdminTrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
