from django.shortcuts import redirect
from django.contrib import messages


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
        if request.user.is_authenticated and True:
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request, 'Nur Trainer dürfen auf diesen Bereich zugreifen.')
            return redirect('trainings-overview')
    return wrapper_func
