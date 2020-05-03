from django.forms import ModelForm
from .models import Training


class NewTrainingForm(ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
