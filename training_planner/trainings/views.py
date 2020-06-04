from operator import itemgetter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth import decorators as auth_decorators
from django.core.mail import send_mass_mail
from django.db.models import Count
from django.db.models.functions import ExtractWeek
from django.utils.text import format_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import dateparser
import datetime
from members.filter import UserStatisticsFilter
from .models import Training, archive_trainings
from .forms import AddTrainingForm, AdminTrainingForm, TrainingForm, \
    TrainingSeriesForm, TrainingArchiveDate, TrainingArchiveDays
from .filter import TrainingFilter, TrainingAdminFilter
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


@trainer_or_admin_only
def all_trainings(request):
    trainings = Training.objects.all().order_by(
        'start', 'title')
    user = request.user
    myFilter = TrainingAdminFilter(request.GET, queryset=trainings)
    trainings = myFilter.qs
    for training in trainings:
        training.can_edit = training.can_edit(user)
        training.passed = training.start < timezone.now()
    context = {'trainings': trainings, 'myFilter': myFilter}
    return render(request, 'trainings/overview.html', context)


@auth_decorators.login_required
def details(request, id):
    training = get_object_or_404(Training, id=id)
    training.can_edit = training.can_edit(request.user)
    training.can_register = training.can_register(request.user)
    training.can_unregister = training.can_unregister(request.user)
    if training.deleted:
        messages.error(
            request,
            _(
                'The training was deleted. To restore the training and enable '
                'editing contact an administrator.'
            ),
        )
    elif training.archived:
        messages.info(
            request,
            _(
                'The training was archived. To reenable editing contact an '
                'administrator.'
            ),
        )

    elif training.before_registration:
        messages.info(
            request,
            format_lazy(
                _('The registration will open on {date} at {time}.'),
                date=training.opendate_as_text,
                time=training.opentime_as_text
            )
        )
    elif training.after_registration:
        messages.info(
            request,
            format_lazy(
                _(
                    'The registration is closed since {date} at {time}. '
                    'For short-term registrations or unregistrations please '
                    'contact the trainer.'
                ),
                date=training.closedate_as_text,
                time=training.closetime_as_text
            )
        )
    context = {'training': training}
    if request.user.is_trainer or request.user.is_administrator:
        return render(request, 'trainings/details_admin.html', context)
    return render(request, 'trainings/details.html', context)


@auth_decorators.login_required
def register(request, id):
    training = get_object_or_404(Training, id=id)
    if training.register(request.user):
        messages.success(
            request, _('You were successfully registered.'))
    else:
        messages.info(request, _('Registration failed.'))
    return redirect('trainings-details', id)


@auth_decorators.login_required
def unregister(request, id):
    training = get_object_or_404(Training, id=id)
    if training.unregister(request.user):
        messages.success(
            request,
            format_lazy(
                _('You have been successfully signed off for {training!s}.'),
                training=training,
            )
        )
    else:
        messages.info(request, _('Sign-off failed.'))
    return redirect('trainings-overview')


@auth_decorators.login_required
def register_as_coordinator(request, id):
    training = get_object_or_404(Training, id=id)
    index = training.register_as_coordinator(request.user)
    msg = {
        0: ('success', _('Thank you for coordinating the entrance.')),
        1: ('info', _('There is already another coordinator registered.')),
        2: ('warning', _('The coordinator cannot be the main instructor.'))
    }
    _simple_message(request, msg, index)
    return redirect('trainings-details', id)


@protect_training
def unregister_coordinator(request, id):
    training = get_object_or_404(Training, id=id)
    training.unregister_coordinator()
    messages.info(request, _('Coordinator removed successfully.'))
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
            messages.success(request, _('Training added successfully.'))
            return redirect(details, training.id)
        else:
            messages.warning(
                request,
                _('Please take care of the highlighted errors.')
            )
    else:
        form = AddTrainingForm(initial={
            'main_instructor': request.user,
            'capacity': 20,
            'duration': 75,
        })
    context = {'form': form, 'title': _('New Training')}
    return render(request, 'trainings/training_form.html', context)


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
            messages.success(request, _('Changes saved successfully.'))
            return redirect(details, id)
        else:
            messages.warning(
                request,
                _('Please take care of the highlighted errors.')
            )
            print(form)
            print(request.POST)
    else:
        form = formClass(instance=training)
    context = {
        'form': form,
        'title': format_lazy(_('Edit {training}'), training=training.title)
    }
    return render(request, 'trainings/training_form.html', context)


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
                    dateparser.parse(date, locales=['de', 'en']),
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
            format_lazy(
                _('Trainings created on {days:d} days.'),
                days=len(dates)
            )
        )
        return redirect(overview)
    training = get_object_or_404(Training, id=id)
    form = TrainingSeriesForm()
    context = {
        'form': form,
        'training': training,
        'title': _('Create Training Series')
    }
    return render(request, 'trainings/training_form.html', context)


@protect_training
def delete(request, id):
    training = get_object_or_404(Training, id=id)
    if request.method == 'POST':
        training.deleted = True
        training.save()
        messages.success(
            request,
            format_lazy(_('{training} has been deleted'), training=training)
        )
        return redirect(overview)
    context = {'item': training, 'title': _('Delete Training')}
    return render(request, 'website/deleteConfirmation.html', context)


@trainer_or_admin_only
def held(request, id=None):
    if request.method == 'POST':
        training_id = request.POST.get('archive', None)
        if training_id is None:
            messages.warning(
                request,
                _('The request contained invalid data. Aborting'),
            )
        training = get_object_or_404(Training, id=training_id)
        if training.can_edit(request.user):
            if training.participants.all().count() > 0 or \
                    training.registered_participants.all().count() == 0:
                training.archived = True
                training.save()
            else:
                messages.info(
                    request,
                    _(
                        'No participants have been recorded for this training.'
                        ' Please record the participants or delete the '
                        'training instead, if it did not take place.'
                    )
                )
        else:
            messages.info(
                request,
                _('You may only access your own trainings.')
            )
    if id is None:
        user = request.user
    elif request.user.id == id:
        return redirect('trainings-held')
    elif not request.user.groups.filter(name='Administrator').exists():
        messages.info(request, _('You may only access your own trainings.'))
        return redirect('trainings-held')
    else:
        user = get_object_or_404(auth.get_user_model(), id=id)
    if not user.is_trainer:
        messages.info(
            request,
            _(
                'You can only view held trainings of members belonging to '
                'the group "Trainer".'
            ),
        )
        return redirect('members-all')
    trainings_main = user.instructor.filter(start__lte=timezone.now() +
                                            datetime.timedelta(minutes=30)) \
        .exclude(archived=True) \
        .exclude(deleted=True) \
        .order_by('-start', 'title')
    trainings_assistant = user.assistant.filter(
        start__lte=timezone.now() + datetime.timedelta(minutes=30)) \
        .exclude(archived=True) \
        .exclude(deleted=True) \
        .order_by('-start', 'title')
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
        group = auth.models.Group.objects.get(
            name='Active Participant'
        )
        group.user_set.add(*participants)
        messages.success(request, _('Changes saved successfully.'))
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
                        _('You cannot send an empty message.')
                    )
                    return render(request, 'trainings/messages.html', context)
            elif key == 'salutation':
                if value == '':
                    salutation = _('Dear')
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
            request,
            format_lazy(
                _('{user:d} messages have been sent.'),
                user=len(user_id)
            )
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
                pass
            if (not isinstance(year, int)) or \
                    datetime.MINYEAR > year or \
                    datetime.MAXYEAR < year:
                messages.info(
                    request,
                    _('No valid year, showing results for this year.')
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


@admin_only
def management(request):
    if request.method == 'POST':
        date = request.POST.get('date', None)
        checked = bool(request.POST.get('checked', False))
        if date is not None:
            archive_trainings(date=date, checked=checked)
        else:
            days = request.POST.get('days', 0)
            weeks = request.POST.get('weeks', 0)
            archive_trainings(
                days=int(days),
                weeks=int(weeks),
                checked=checked
            )
    form1 = TrainingArchiveDate()
    form2 = TrainingArchiveDays()
    context = {
        'form1': form1,
        'form2': form2,
    }
    return render(request, 'trainings/training_management.html', context)
