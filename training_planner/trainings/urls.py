from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views as trainings

urlpatterns = [
    path('', trainings.overview, name='trainings-overview'),
    path('<int:id>/', trainings.details, name='trainings-details'),
    path(f'<int:id>/{_("register")}/',
         trainings.register, name='trainings-register'),
    path(f'<int:id>/{_("unregister")}/', trainings.unregister,
         name='trainings-unregister'),
    path(f'<int:id>/{_("coordinator")}/{_("register")}/',
         trainings.register_as_coordinator,
         name='trainings-register-coordinator'),
    path(f'<int:id>/{_("coordinator")}/{_("unregister")}',
         trainings.unregister_coordinator,
         name='trainings-unregister-coordinator'),
    path(f'{_("create")}/', trainings.create, name='trainings-create'),
    path(f'<int:id>/{_("edit")}/', trainings.edit, name='trainings-edit'),
    path(f'<int:id>/{_("delete")}/',
         trainings.delete, name='trainings-delete'),
    path(f'<int:id>/{_("message")}/',
         trainings.message, name='trainings-message'),
    path(f'<int:id>/{_("series")}/', trainings.make_training_series,
         name='trainings-series'),
    path(f'{_("control")}/', trainings.held, name='trainings-held'),
    path(f'<int:id>/{_("control")}/', trainings.controlling,
         name='trainings-controlling'),
    path(f'{_("control")}/<int:id>/', trainings.held,
         name='trainings-held-trainer'),
    path(f'{_("participation")}/', trainings.participation_view,
         name='trainings-participation'),
]
