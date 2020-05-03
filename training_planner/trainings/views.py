from django.shortcuts import render
from .models import Training
from .forms import NewTrainingForm
# Create your views here.


def overview(request):
    trainings = Training.objects.all()
    context = {'trainings': trainings}
    return render(request, 'trainings/overview.html', context)


def details(request, id):
    training = Training.objects.get(id=id)
    context = {'training': training}
    return render(request, 'trainings/details.html', context)


def create(request):
    form = NewTrainingForm
    context = {'form': form}
    return render(request, 'trainings/create.html', context)
