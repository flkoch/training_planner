from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import decorators as auth_decorators
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from trainings import decorators
from .filter import UserFilter
from .forms import CreateUserForm
from .models import User

# Create your views here.


@auth_decorators.login_required(login_url='login')
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
        'user': user,
        'edit_link': reverse('account-edit'),
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj,
    }
    return render(request, 'members/details.html', context)


@auth_decorators.login_required(login_url='login')
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
        'user': user,
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
            if not user.initials:
                user.initials = user.get_initials
            user.save()
            user.groups.add(Group.objects.get(name='Participant'))
            form.save_m2m()
            messages.success(request, 'Der Account wurde erstellt.')
            return redirect(login)
    context = {'form': form}
    return render(request, 'members/register.html', context)


@auth_decorators.permission_required('members.view_user')
def all(request):
    users = User.objects.all().exclude(groups__name='System')
    myFilter = UserFilter(request.GET, queryset=users)
    users = myFilter.qs
    context = {'users': users, 'myFilter': myFilter}
    return render(request, 'members/listview.html', context)


@auth_decorators.permission_required('members.view_user')
def details(request, id):
    user = User.objects.get(id=id)
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
        'user': user,
        'edit_link': reverse('member-edit', args=[id]),
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj,
    }
    return render(request, 'members/details.html', context)


@auth_decorators.permission_required('members.edit_user')
def edit(request, id):
    user = User.objects.get(id=id)
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
        'user': user,
        'edit_link': reverse('member-edit', args=[id]),
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj,
    }
    messages.info(
        request,
        'Das Bearbeiten der Nutzerdaten ist aktuell leider noch nicht möglich.'
    )
    return render(request, 'members/editForm.html', context)
