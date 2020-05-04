from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import decorators as auth_decorators
from trainings import decorators
from .forms import CreateUserForm

# Create your views here.


@auth_decorators.login_required(login_url='login')
def account(request):
    return render(request, 'members/account.html')


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
            messages.info(
                request, "Benutzername und Passwort gehören zu"
                " keinem gültigen Benutzer.")
    context = {'username': username}
    return render(request, 'members/login.html', context)


@decorators.unauthorised_user
def logout(request):
    auth.logout(request)
    return redirect('/trainings')


@decorators.unauthorised_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Der Account wurde erstellt.')
            return redirect(login)
    context = {'form': form}
    return render(request, 'members/register.html', context)
