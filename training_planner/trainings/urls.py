from django.urls import path
from . import views as trainings

urlpatterns = [
    path('', trainings.overview, name='trainings-overview'),
    path('<int:id>', trainings.details, name='trainings-details'),
    path('<int:id>/anmelden', trainings.register, name='trainings-register'),
    path('<int:id>/abmelden', trainings.unregister,
         name='trainings-unregister'),
    path('<int:id>/koordinator/anmelden', trainings.register_as_coordinator,
         name='trainings-register-coordinator'),
    path('<int:id>/koordinator/abmelden', trainings.unregister_coordinator,
         name='trainings-unregister-coordinator'),
    path('erstellen', trainings.create, name='trainings-create'),
    path('<int:id>/bearbeiten', trainings.edit, name='trainings-edit'),
    path('<int:id>/entfernen', trainings.delete, name='trainings-delete'),
    path('<int:id>/nachricht', trainings.message, name='trainings-message'),
    path('<int:id>/serie', trainings.make_training_series,
         name='trainings-series'),
    path('kontrolle', trainings.held, name='trainings-held'),
    path('<int:id>/kontrolle', trainings.controlling,
         name='trainings-controlling'),
    path('kontrolle/<int:id>', trainings.held,
         name='trainings-held-trainer'),
    path('teilnahme', trainings.participation_view,
         name='trainings-participation'),
]
