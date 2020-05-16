from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import decorators as auth_decorators
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from trainings import decorators
from .filter import UserFilter
from .forms import CreateUserForm
from .models import User, check_active_participants, check_active_trainers, \
    check_trainers

# Create your views here.


@auth_decorators.login_required
def account(request):
    user = request.user
    reg_trainings = user.trainings_registered.filter(
        start__gte=timezone.now()).order_by('start')
    part_trainings = user.trainings.filter(
        start__lte=timezone.now()).order_by('-start')
    paginator = Paginator(part_trainings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page((page_number))
    context = {
        'page_user': user,
        'edit_link': reverse('account-edit'),
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj,
    }
    return render(request, 'members/details.html', context)


@auth_decorators.login_required
def account_edit(request):
    user = request.user
    reg_trainings = user.trainings_registered.filter(
        start__gte=timezone.now()).order_by('start')
    part_trainings = user.trainings.filter(
        start__lte=timezone.now()).order_by('-start')
    paginator = Paginator(part_trainings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page((page_number))
    context = {
        'page_user': user,
        'edit_link': reverse('account-edit'),
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj,
    }
    messages.info(
        request,
        'Das Bearbeiten der Nutzerdaten ist aktuell leider noch nicht möglich.'
    )
    return render(request, 'members/editForm.html', context)


@decorators.unauthorised_user
def login(request):
    username = ''
    if request.method == 'POST':
        user = auth.authenticate(request,
                                 username=request.POST.get('username'),
                                 password=request.POST.get('password'))
        if user is not None:
            auth.login(request, user)
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('/trainings')
        else:
            messages.info(request, "Benutzername und Passwort gehören zu"
                          " keinem gültigen Benutzer.")
    context = {'username': username}
    return render(request, 'members/login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('/trainings')


@decorators.unauthorised_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not (user.initials and user.initials.strip()):
                user.initials = user.get_initials()
            user.save()
            user.groups.add(get_object_or_404(
                auth.models.Group, name='Participant'))
            form.save_m2m()
            subject = 'Anmeldung auf training.judo-club-uster.ch'
            message = str(
                f'Hallo {user.first_name},\r\nWir freuen uns, dass Du Dich auf'
                ' unserer Plattform angemeldet hast, um auch künftig an den '
                'angebotenen Trainings teilnehmen zu können.\r\nUm an den '
                'Trainings teilnehmen zu dürfen, musst Du folgende Punkte '
                'erfüllen:\r\n1) Du musst für das entsprechende Training '
                'angemeldet sein.\r\n2) Du musst das Zutrittsformular '
                'ausfüllen und in jedes Training mitbringen.\r\n\r\nAlso '
                'eigentlich ganz einfach. Wenn Du trotzdem Fragen hast, darfst'
                ' Du Dich gerne bei den Trainern oder unter info@jcu.ch '
                'melden.\r\nAusserdem brauchen wir für jedes Training einen '
                'Koordinator oder eine Koordinatorin. Wenn Du dies also hin '
                'und wieder übernehmen könntest, profitieren alle, die gerne '
                'trainieren wollen.\r\n\r\nViel Spass im Training wünscht Dir '
                'das JCU Trainer-Team'
            )
            send_mail(subject, message, 'no-reply@judo-club-uster.ch',
                      [user.email])
            messages.success(
                request,
                'Der Account wurde erstellt. '
                'Bitte überprüfe Deinen Posteingang.'
            )
            return redirect(login)
    context = {'form': form}
    return render(request, 'members/register.html', context)


@auth_decorators.permission_required('members.view_user')
def all(request):
    users = User.objects.all().exclude(groups__name='System') \
        .order_by('last_name', 'first_name')
    myFilter = UserFilter(request.GET, queryset=users)
    users = myFilter.qs
    context = {'users': users, 'myFilter': myFilter}
    return render(request, 'members/overview.html', context)


@auth_decorators.permission_required('members.view_user')
def details(request, id):
    user = get_object_or_404(auth.get_user_model(), id=id)
    if request.user == user:
        return redirect('account')
    reg_trainings = user.trainings_registered.filter(
        start__gte=timezone.now()).order_by('start')
    part_trainings = user.trainings.filter(
        start__lte=timezone.now()).order_by('-start')
    paginator = Paginator(part_trainings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page((page_number))
    context = {
        'page_user': user,
        'edit_link': reverse('member-edit', args=[id]),
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj,
    }
    return render(request, 'members/details.html', context)


@auth_decorators.permission_required('members.edit_user')
def edit(request, id):
    user = get_object_or_404(auth.get_user_model(), id=id)
    if request.user == user:
        return redirect('account-edit')
    reg_trainings = user.trainings_registered.filter(
        start__gte=timezone.now()).order_by('start')
    part_trainings = user.trainings.filter(
        start__lte=timezone.now()).order_by('-start')
    paginator = Paginator(part_trainings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page((page_number))
    context = {
        'page_user': user,
        'edit_link': reverse('member-edit', args=[id]),
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj,
    }
    messages.info(
        request,
        'Das Bearbeiten der Nutzerdaten ist aktuell leider noch nicht möglich.'
    )
    return render(request, 'members/editForm.html', context)


@decorators.admin_only
def user_management(request):
    if request.method == 'POST':
        print(request.POST)
        if 'check_active_participants' in request.POST:
            check_active_participants(weeks=15)
            messages.success(request, 'Aktive Teilnehmer aktualisiert')
        elif 'check_active_trainers' in request.POST:
            check_active_trainers(weeks=15)
            messages.success(request, 'Aktive Trainer aktualisiert')
        elif 'check_trainers' in request.POST:
            check_trainers(weeks=15)
            messages.success(request, 'Trainer aktualisiert')
    return render(request, 'members/user_management.html')
