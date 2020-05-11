from django.shortcuts import redirect
from django.contrib import messages
from .models import Training


def unauthorised_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('trainings-overview')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator


def trainer_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and \
                request.user.groups.filter(name='Trainer').exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request, 'Nur Trainer dürfen auf diesen Bereich zugreifen.')
            return redirect('trainings-overview')
    return wrapper_func


def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and \
                request.user.groups.filter(name='Administrator').exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request,
                'Nur Administratoren dürfen auf diesen Bereich zugreifen.'
            )
            return redirect('trainings-overview')
    return wrapper_func


def protect_training(view_func):
    def wrapper_func(request, *args, **kwargs):
        training = Training.objects.get(id=kwargs.get('id'))
        if training.can_edit(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request, 'Nur die zuständigen Trainer und Administratoren '
                'dürfen auf diesen Bereich zugreifen.')
            return redirect('trainings-overview')
    return wrapper_func
