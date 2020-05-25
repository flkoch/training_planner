from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views as trainings

urlpatterns = [
    path('', trainings.overview, name='trainings-overview'),
    path('<int:id>/', trainings.details, name='trainings-details'),
    path(_('<int:id>/register/'),
         trainings.register, name='trainings-register'),
    path(_('<int:id>/unregister/'), trainings.unregister,
         name='trainings-unregister'),
    path(_('<int:id>/coordinator/register/'),
         trainings.register_as_coordinator,
         name='trainings-register-coordinator'),
    path(_('<int:id>/coordinator/unregister/'),
         trainings.unregister_coordinator,
         name='trainings-unregister-coordinator'),
    path(_('create/'), trainings.create, name='trainings-create'),
    path(_('<int:id>/edit/'), trainings.edit, name='trainings-edit'),
    path(_('<int:id>/delete/'),
         trainings.delete, name='trainings-delete'),
    path(_('<int:id>/message/'),
         trainings.message, name='trainings-message'),
    path(_('<int:id>/series/'), trainings.make_training_series,
         name='trainings-series'),
    path(_('control/'), trainings.held, name='trainings-held'),
    path(_('<int:id>/control/'), trainings.controlling,
         name='trainings-controlling'),
    path(_('control/<int:id>/'), trainings.held,
         name='trainings-held-trainer'),
    path(_('participation/'), trainings.participation_view,
         name='trainings-participation'),
]
