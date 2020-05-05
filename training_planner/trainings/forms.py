from django.forms import ModelForm
from .models import Training


class AddTrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['deleted', 'archived']


class TrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['deleted', 'archived']


class AdminTrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
