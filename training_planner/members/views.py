from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import decorators as auth_decorators
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from trainings import decorators

from .filter import UserFilter
from .forms import ChangeUserForm, CreateUserForm
from .models import (User, check_active_participants, check_active_trainers,
                     check_trainers)

# Create your views here.


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
            messages.info(
                request,
                _('Username and password do not match a valid user.')
            )
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
            subject = format_lazy(
                _('Registration on {website}'),
                website=settings.ALLOWED_HOSTS[0] if len(
                    settings.ALLOWED_HOSTS) > 0 else 'TrainingPlanner'
            )
            message = format_lazy(
                _(
                    'Hi {name},\nWe are happy to have you on our '
                    'platform, which allows you to register for and '
                    'participate in offered training sessions.\nIf you have '
                    'questions on the requirements for participation contact '
                    'the instructor or the administration.\nFor each Training '
                    'we need a coordinator. If you could do this from time to '
                    'time everyone will enjoy the experience.\nEnjoy your '
                    'trainings\nYour Instructor team'
                ),
                name=user.first_name
            )
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            email.send()
            messages.success(
                request,
                _('The account has been created. '
                  'Please check your inbox.')
            )
            return redirect(login)
    context = {
        'title': _('Register'),
        'form': form,
    }
    return render(request, 'members/user_form.html', context)


@auth_decorators.permission_required('members.view_user')
def all(request):
    users = User.objects.all().exclude(groups__name='System') \
        .order_by('last_name', 'first_name')
    myFilter = UserFilter(request.GET, queryset=users)
    users = myFilter.qs
    context = {'users': users, 'myFilter': myFilter}
    return render(request, 'members/overview.html', context)


@auth_decorators.login_required
def details(request, id=None):
    if id is None:
        user = request.user
        edit_link = reverse('account-edit')
    else:
        user = get_object_or_404(auth.get_user_model(), id=id)
        if user == request.user:
            return redirect('account')
        elif not request.user.has_perm('members.view_user'):
            messages.info(
                request,
                _('Only trainers and administrators may access this area.')
            )
            return redirect('trainings-overview')
        edit_link = reverse('member-edit', args=[id])
    reg_trainings = user.trainings_registered.filter(
        start__gte=timezone.now()).order_by('start')
    part_trainings = user.trainings.filter(
        start__lte=timezone.now()).order_by('-start')
    visited_trainings = user.visited_trainings.all()
    paginator = Paginator(part_trainings, 10)
    page_number = request.GET.get('page1')
    page_obj1 = paginator.get_page((page_number))
    paginator = Paginator(visited_trainings, 10)
    page_number = request.GET.get('page2')
    page_obj2 = paginator.get_page((page_number))
    context = {
        'page_user': user,
        'edit_link': edit_link,
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj1,
        'visited_trainings': page_obj2,
    }
    return render(request, 'members/details.html', context)


@auth_decorators.login_required
def edit(request, id=None):
    if id is None:
        user = request.user
    else:
        user = get_object_or_404(auth.get_user_model(), id=id)
        if user == request.user:
            return redirect('account-edit')
        elif not request.user.has_perm('members.edit'):
            messages.info(
                request,
                _('Only trainers and administrators may access this area.')
            )
            return redirect('trainings-overview')
    if request.method == 'POST':
        form = ChangeUserForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.initials = ''.join(
                c for c in form.cleaned_data['initials'] if c.isalpha()
            ).upper()
            user.birth_date = form.cleaned_data['birth_date']
            user.save()
            if id is None:
                return redirect('account')
            else:
                return redirect('member-details', id=id)
    form = ChangeUserForm(instance=user)
    context = {
        'title': _('Edit User'),
        'form': form,
    }
    return render(request, 'members/user_form.html', context)


@auth_decorators.login_required
@decorators.admin_only
def user_management(request):
    if request.method == 'POST':
        print(request.POST)
        if 'check_active_participants' in request.POST:
            check_active_participants(weeks=15)
            messages.success(request, _('Update Active Participants'))
        elif 'check_active_trainers' in request.POST:
            check_active_trainers(weeks=15)
            messages.success(request, _('Update Active Trainer'))
        elif 'check_trainers' in request.POST:
            check_trainers(weeks=15)
            messages.success(request, _('Update Trainer'))
    return render(request, 'members/user_management.html')
