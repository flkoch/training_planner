from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Training
from .forms import AddTrainingForm, TrainingForm
# Create your views here.


def overview(request, message=None):
    trainings = Training.objects.filter(start__date__gt=timezone.now()) \
        .exclude(archived=True) \
        .exclude(deleted=True) \
        .order_by('start', 'title')
    context = {'trainings': trainings, 'message': message}
    return render(request, 'trainings/overview.html', context)


def details(request, id):
    training = Training.objects.get(id=id)
    context = {'training': training}
    return render(request, 'trainings/details.html', context)


def create(request):
    if request.method == 'POST':
        form = AddTrainingForm(request.POST)
        if form.is_valid():
            form.save()
            # message = {'text': "Training erfolgreich hinzugefügt.",
            #    'type': "success"}
            return redirect(overview)
    form = AddTrainingForm
    context = {'form': form, 'title': 'Neues Training'}
    return render(request, 'trainings/trainingForm.html', context)


def edit(request, id):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            form.save()
            # message = {'text': "Änderungen erfolgreich gespeichert",
            #    'type': "success"}
            return redirect(overview)
    training = Training.objects.get(id=id)
    form = TrainingForm(instance=training)
    context = {'form': form, 'title': f"{training.name} bearbeiten"}
    return render(request, 'trainings/trainingForm.html', context)


def delete(request, id):
    training = Training.objects.get(id=id)
    if request.method == 'POST':
        training.deleted = True
        # message = {'text': f"<em>{training}</em> wurde gelöscht",
        #    'type': "success"}
        return redirect(overview)
    context = {'item': training, 'title': 'Training löschen'}
    return render(request, 'website/deleteConfirmation.html', context)
