from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
import datetime
from .models import Training
from .forms import AddTrainingForm, TrainingForm
from .filter import TrainingFilter
from .decorators import trainer_only, protect_training
# Create your views here.


def _simple_message(request, msg, index=0):
    kind, message = msg.get(index, ('info', 'no message'))
    if kind == 'warning':
        messages.warning(request, message)
    elif kind in ['danger', 'error']:
        messages.error(request, message)
    elif kind == 'success':
        messages.success(request, message)
    elif kind == 'debug':
        messages.debug(request, message)
    else:
        messages.info(request, message)


def overview(request):
    trainings = Training.objects.filter(start__gte=timezone.now()) \
        .exclude(start__gte=timezone.now() + datetime.timedelta(days=14)) \
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
    training.can_register = training.can_register(request.user)
    training.can_unregister = training.can_unregister(request.user)
    context = {'training': training}
    if request.user.groups.filter(name="Trainer").exists():
        return render(request, 'trainings/details_admin.html', context)
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


@auth_decorators.login_required(login_url='login')
def register_as_coordinator(request, id):
    training = Training.objects.get(id=id)
    index = training.register_as_coordinator(request.user)
    msg = {
        0: ('success', 'Vielen Dank, dass Du den Einlass koordinierst.'),
        1: ('info', 'Es ist bereits ein anderer Koordinator angemeldet.'),
        2: ('warning', 'Der Koordinator kann nicht der Haupt-Trainer sein.'),
    }
    _simple_message(request, msg, index)
    return redirect('trainings-details', id)


@protect_training
def unregister_as_coordinator(request, id):
    training = Training.objects.get(id=id)
    training.unregister_as_coordinator()
    messages.info(request, "Koordinator erfolgreich entfernt.")
    return redirect('trainings-details', id)


@trainer_only
def create(request):
    if request.method == 'POST':
        form = AddTrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.registration_close = training.start - \
                datetime.timedelta(2)
            training.registration_open = timezone.now() - \
                datetime.timedelta(14)
            training.save()
            form.save_m2m()
            messages.success(request, 'Training erfolgreich hinzugefügt.')
            return redirect(details, training.id)
    else:
        form = AddTrainingForm()
    context = {'form': form, 'title': 'Neues Training'}
    return render(request, 'trainings/trainingForm.html', context)


@protect_training
def edit(request, id):
    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=Training.objects.get(id=id))
        if form.is_valid():
            form.save()
            messages.success(request, 'Änderungen erfolgreich gespeichert')
            return redirect(details, id)
    training = Training.objects.get(id=id)
    form = TrainingForm(instance=training)
    context = {'form': form, 'title': f"{training.title} bearbeiten"}
    return render(request, 'trainings/trainingForm.html', context)


@protect_training
def delete(request, id):
    training = Training.objects.get(id=id)
    if request.method == 'POST':
        training.deleted = True
        training.save()
        # message = {'text': f"<em>{training}</em> wurde gelöscht",
        #    'type': "success"}
        return redirect(overview)
    context = {'item': training, 'title': 'Training löschen'}
    return render(request, 'website/deleteConfirmation.html', context)
