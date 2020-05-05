from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from .models import Training
from .forms import AddTrainingForm, TrainingForm
from .filter import TrainingFilter
from .decorators import trainer_only
# Create your views here.


def overview(request):
    trainings = Training.objects.filter(start__date__gt=timezone.now()) \
        .exclude(archived=True) \
        .exclude(deleted=True) \
        .order_by('start', 'title')
    myFilter = TrainingFilter(request.GET, queryset=trainings)
    trainings = myFilter.qs
    for training in trainings:
        training.can_edit = training.can_edit(request.user)
        training.is_registered = training.is_registered(request.user)
    context = {'trainings': trainings, 'myFilter': myFilter}
    return render(request, 'trainings/overview.html', context)


@auth_decorators.login_required(login_url='login')
def details(request, id):
    training = Training.objects.get(id=id)
    training.can_edit = training.can_edit(request.user)
    training.can_unregister = training.can_unregister(request.user)
    context = {'training': training}
    return render(request, 'trainings/details.html', context)


@auth_decorators.login_required(login_url='login')
def register(request, id):
    training = Training.objects.get(id=id)
    if training.register(request.user):
        messages.success(
            request, f'Du wurdest erfolgreich angemeldet.')
    else:
        messages.info(request, 'Anmeldung ist fehlgeschlagen.')
    return redirect('trainings-details', id)


@auth_decorators.login_required(login_url='login')
def unregister(request, id):
    training = Training.objects.get(id=id)
    if training.unregister(request.user):
        messages.success(
            request, f'Du wurdest erfolgreich von {training} abgemeldet.')
    else:
        messages.info(request, 'Abmelden ist fehlgeschlagen.')
    return redirect('trainings-overview')


@trainer_only
def create(request):
    if request.method == 'POST':
        form = AddTrainingForm(request.POST)
        if form.is_valid():
            id = form.save().id
            messages.success(request, 'Training erfolgreich hinzugefügt.')
            return redirect(details, id)
    form = AddTrainingForm
    context = {'form': form, 'title': 'Neues Training'}
    return render(request, 'trainings/trainingForm.html', context)


@trainer_only
def edit(request, id):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            form.save(instance=Training.objects.get(id=id))
            messages.success(request, 'Änderungen erfolgreich gespeichert')
            return redirect(details, id)
    training = Training.objects.get(id=id)
    form = TrainingForm(instance=training)
    context = {'form': form, 'title': f"{training.title} bearbeiten"}
    return render(request, 'trainings/trainingForm.html', context)


@trainer_only
def delete(request, id):
    training = Training.objects.get(id=id)
    if request.method == 'POST':
        training.deleted = True
        # message = {'text': f"<em>{training}</em> wurde gelöscht",
        #    'type': "success"}
        return redirect(overview)
    context = {'item': training, 'title': 'Training löschen'}
    return render(request, 'website/deleteConfirmation.html', context)
