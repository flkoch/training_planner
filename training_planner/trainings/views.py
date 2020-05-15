from operator import itemgetter
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages, auth
from django.contrib.auth import decorators as auth_decorators
from django.core.mail import send_mass_mail
from django.db.models import Count
from django.db.models.functions import ExtractWeek
import datetime
from members.filter import UserStatisticsFilter
from .models import Training
from .forms import AddTrainingForm, AdminTrainingForm, TrainingForm, \
    TrainingSeriesForm
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


@auth_decorators.login_required
def details(request, id):
    training = get_object_or_404(Training, id=id)
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


@auth_decorators.login_required
def register(request, id):
    training = get_object_or_404(Training, id=id)
    if training.register(request.user):
        messages.success(
            request, f'Du wurdest erfolgreich angemeldet.')
    else:
        messages.info(request, 'Anmeldung ist fehlgeschlagen.')
    return redirect('trainings-details', id)


@auth_decorators.login_required
def unregister(request, id):
    training = get_object_or_404(Training, id=id)
    if training.unregister(request.user):
        messages.success(
            request, f'Du wurdest erfolgreich von {training} abgemeldet.')
    else:
        messages.info(request, 'Abmelden ist fehlgeschlagen.')
    return redirect('trainings-overview')


@auth_decorators.login_required
def register_as_coordinator(request, id):
    training = get_object_or_404(Training, id=id)
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
    training = get_object_or_404(Training, id=id)
    training.unregister_coordinator()
    messages.info(request, "Koordinator erfolgreich entfernt")
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
            messages.success(request, 'Training erfolgreich hinzugefügt')
            return redirect(details, training.id)
        else:
            messages.warning((request, 'Bitte die angezeigten Fehler beheben'))
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
    if request.user.is_administrator:
        formClass = AdminTrainingForm
    else:
        formClass = TrainingForm
    training = get_object_or_404(Training, id=id)
    if request.method == 'POST':
        form = formClass(request.POST, instance=training)
        if form.is_valid():
            form.save()
            messages.success(request, 'Änderungen erfolgreich gespeichert')
            return redirect(details, id)
        else:
            messages.warning((request, 'Bitte die angezeigten Fehler beheben'))
    else:
        form = formClass(instance=training)
    context = {'form': form, 'title': f"{training.title} bearbeiten"}
    return render(request, 'trainings/trainingForm.html', context)


@protect_training
def make_training_series(request, id):
    if request.method == 'POST':
        training = get_object_or_404(Training, id=id)
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
    training = get_object_or_404(Training, id=id)
    form = TrainingSeriesForm()
    context = {
        'form': form,
        'training': training,
        'title': 'Neue Trainings Serie'
    }
    return render(request, 'trainings/trainingForm.html', context)


@protect_training
def delete(request, id):
    training = get_object_or_404(Training, id=id)
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
        user = get_object_or_404(auth.get_user_model(), id=id)
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
    training = get_object_or_404(Training, id=id)
    if request.method == 'POST':
        participants = [int(user_id) for user_id, value in request.POST.items()
                        if 'participated' in value]
        training.participants.clear()
        training.participants.add(*participants)
        group = auth.models.Group.objects.get(name='Active Participant')
        group.user_set.add(*participants)
        messages.success(request, 'Änderungen gespeichert')
    context = {'training': training}
    return render(request, 'trainings/details_controlling.html', context)


@protect_training
def message(request, id):
    training = get_object_or_404(Training, id=id)
    context = {
        'training': training,
    }
    if request.method == 'POST':
        user_id = []
        from_email = request.user.email
        for key, value in request.POST.items():
            if key == 'message':
                message = value
                if message.rstrip == '':
                    messages.warning(
                        request,
                        'Eine leere Nachricht kann nicht gesendet werden'
                    )
                    return render(request, 'trainings/messages.html', context)
            elif key == 'salutation':
                if value == '':
                    salutation = 'Hallo'
                else:
                    salutation = value.rstrip()
            elif key == 'subject':
                subject = value
            elif 'send_message' in value:
                user_id.append(key)
        mails = [
            [subject, salutation + ' ' + user.first_name + ',\r\n' + message,
             from_email, [user.email]] for user in
            [auth.get_user_model().objects.get(id=id) for id in user_id]]
        mails = tuple([tuple(mail) for mail in mails])
        send_mass_mail(mails)
        messages.success(
            request, f'Es wurden {len(user_id)} Nachrichten versendet.'
        )
        return redirect('trainings-details', id)
    return render(request, 'trainings/message.html', context)


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
