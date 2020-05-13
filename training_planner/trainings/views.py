from operator import itemgetter
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages, auth
from django.contrib.auth import decorators as auth_decorators
from django.db.models import Count
from django.db.models.functions import ExtractWeek
import datetime
from members.filter import UserStatisticsFilter
from .models import Training
from .forms import AddTrainingForm, TrainingForm, TrainingSeriesForm
from .filter import TrainingFilter
from .decorators import trainer_only, protect_training, admin_only, \
    trainer_or_admin_only
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
    if request.user.is_authenticated and request.user.is_trainer:
        trainings = Training.objects.filter(start__gte=timezone.now() -
                                            datetime.timedelta(hours=2))
    else:
        trainings = Training.objects.filter(start__gte=timezone.now() -
                                            datetime.timedelta(hours=2)) \
            .exclude(start__gte=timezone.now() + datetime.timedelta(days=14))
    trainings = trainings.exclude(archived=True) \
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
    if training.before_registration:
        messages.info(
            request, f'Die Anmeldung wird am {training.opendate_as_text} um '
            f'{training.opentime_as_text} Uhr geöffnet.')
    elif training.after_registration:
        messages.info(
            request, f'Die Anmeldung ist seit dem {training.closedate_as_text}'
            f' um {training.closetime_as_text} geschlossen. Für kurzfristige '
            'An- oder Abmeldungen kontaktiere bitte den zuständigen Trainer.')
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
def unregister_coordinator(request, id):
    training = Training.objects.get(id=id)
    training.unregister_coordinator()
    messages.info(request, "Koordinator erfolgreich entfernt.")
    return redirect('trainings-details', id)


@trainer_only
def create(request):
    if request.method == 'POST':
        form = AddTrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.set_registration_times()
            training.save()
            form.save_m2m()
            messages.success(request, 'Training erfolgreich hinzugefügt.')
            return redirect(details, training.id)
    else:
        form = AddTrainingForm(initial={
            'main_instructor': request.user,
            'capacity': 10,
            'duration': 45,
        })
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
def make_training_series(request, id):
    if request.method == 'POST':
        training = Training.objects.get(id=id)
        training.coordinator = None
        instructors = [e.id for e in training.instructor.all()]
        target_groups = [e.id for e in training.target_group.all()]
        dates = request.POST['dates'].split(',')
        for date in dates:
            training.pk = None
            training.start = timezone.make_aware(
                datetime.datetime.combine(
                    datetime.datetime.strptime(date, '%d.%m.%Y'),
                    timezone.make_naive(training.start).time()
                ),
                timezone.get_current_timezone()
            )
            training.deleted = False
            training.archived = False
            training.set_registration_times()
            training.save()
            training.instructor.add(*instructors)
            training.target_group.add(*target_groups)
        messages.success(
            request,
            f'Trainings an {len(dates)} Tagen erstellt.'
        )
        return redirect(overview)
    training = Training.objects.get(id=id)
    form = TrainingSeriesForm()
    context = {
        'form': form,
        'training': training,
        'title': 'Neue Trainings Serie'
    }
    return render(request, 'trainings/trainingForm.html', context)


@protect_training
def delete(request, id):
    training = Training.objects.get(id=id)
    if request.method == 'POST':
        training.deleted = True
        training.save()
        messages.success(request, f'{training} wurde gelöscht')
        return redirect(overview)
    context = {'item': training, 'title': 'Training löschen'}
    return render(request, 'website/deleteConfirmation.html', context)


@trainer_or_admin_only
def held(request, id=None):
    if id is None:
        user = request.user
    elif not request.user.groups.filter(name='Administrator').exists():
        messages.info(request, 'Zugriff nur auf eigene Trainings.')
        return redirect('trainings-held')
    else:
        user = auth.get_user_model().objects.get(id=id)
        if user == request.user:
            return redirect('trainings-held')
    trainings_main = user.instructor.filter(start__lte=timezone.now() +
                                            datetime.timedelta(minutes=30)) \
        .exclude(start__lte=timezone.now() - datetime.timedelta(days=7)) \
        .exclude(deleted=True)\
        .order_by('start', 'title')
    trainings_assistant = user.assistant.filter(
        start__lte=timezone.now() + datetime.timedelta(minutes=30)) \
        .exclude(start__lte=timezone.now() - datetime.timedelta(days=7)) \
        .exclude(deleted=True)
    context = {
        'title': str(user),
        'trainings_main': trainings_main,
        'trainings_assistant': trainings_assistant
    }
    return render(request, 'trainings/overview_held_trainings.html', context)


@protect_training
def controlling(request, id):
    training = Training.objects.get(id=id)
    if request.method == 'POST':
        participants = [int(user_id) for user_id, value in request.POST.items()
                        if 'participated' in value]
        training.participants.clear()
        training.participants.add(*participants)
        messages.success(request, "Änderungen gespeichert")
    context = {'training': training}
    return render(request, 'trainings/details_controlling.html', context)


@admin_only
def participation_view(request, year=None):
    if year is None:
        if 'year' in request.GET and request.GET['year'] != '':
            try:
                year = int(request.GET['year'])
            except ValueError:
                print("ValueError")
                pass
            if (not isinstance(year, int)) or \
                    datetime.MINYEAR > year or \
                    datetime.MAXYEAR < year:
                messages.info(
                    request,
                    'Ungültiges Jahr, zeige Werte für aktuelles Kalendarjahr.'
                )
                year = timezone.now().year
        else:
            year = timezone.now().year
    users = auth.get_user_model().objects.filter(
        groups__name='Active Participant'
    ).filter(trainings__start__year=year).annotate(
        total_trainings=Count('trainings')
    ).annotate(
        week_num=ExtractWeek('trainings__start')
    ).values(
        'id',
        'first_name',
        'last_name',
        'username',
        'total_trainings',
        'week_num'
    ).annotate(
        count=Count('week_num')
    ).order_by('id')
    myFilter = UserStatisticsFilter(request.GET, queryset=users)
    users = myFilter.qs
    new_users = []
    for user in users:
        if len(new_users) != 0 and user['id'] == new_users[-1]['id']:
            new_users[-1]['week_' + str(user['week_num'])] = user['count']
            new_users[-1]['total_trainings'] += user['total_trainings']
        else:
            new_users.append({
                'id': user['id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'username': user['username'],
                'total_trainings': user['total_trainings'],
                'week_' + str(user['week_num']): user['count'],
            })
    new_users.sort(key=itemgetter('first_name'))
    new_users.sort(key=itemgetter('last_name'))
    context = {
        'users': new_users,
        'myFilter': myFilter,
        'year': year,
    }
    return render(request, 'trainings/participation_view.html', context)
