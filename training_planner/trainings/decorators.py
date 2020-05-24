from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
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
            request.user.groups.filter(name='Trainer') \
                .exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request, _('Only trainers may access this area.'))
            return redirect('trainings-overview')
    return wrapper_func


def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and \
            request.user.groups.filter(name='Administrator') \
                .exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request,
                _('Only administrators may access this area.')
            )
            return redirect('trainings-overview')
    return wrapper_func


def trainer_or_admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and \
                request.user.groups.filter(name__in=[
                    'Trainer', 'Administrator',
                ]).exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request,
                _('Only trainers and administrators may access this area.')
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
                request,
                _('Only administrators and the respective trainers may access '
                  'this area.')
            )
            return redirect('trainings-overview')
    return wrapper_func
