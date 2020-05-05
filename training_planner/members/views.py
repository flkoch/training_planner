from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import decorators as auth_decorators
from django.contrib.auth.models import Group
from trainings import decorators
from .forms import CreateUserForm
from .models import User
from .filter import UserFilter

# Create your views here.


@auth_decorators.login_required(login_url='login')
def account(request):
    return render(request, 'members/account.html')


@decorators.unauthorised_user
def login(request):
    username = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
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
            user = form.save()
            user.groups.add(Group.objects.get(name='Participant'))
            user.initials = user.get_initials()
            messages.success(request, 'Der Account wurde erstellt.')
            return redirect(login)
    context = {'form': form}
    return render(request, 'members/register.html', context)


@auth_decorators.permission_required('members.view_user')
def all(request):
    users = User.objects.all()
    myFilter = UserFilter(request.GET, queryset=users)
    users = myFilter.qs
    context = {'users': users, 'myFilter': myFilter}
    return render(request, 'members/listview.html', context)


@auth_decorators.permission_required('members.view_user')
def details(request, id):
    user = User.objects.get(id=id)
    context = {'user': user}
    return render(request, 'members/details.html', context)
