from django.urls import path
from . import views as trainings

urlpatterns = [
    path('', trainings.overview, name="trainings-overview"),
    path('<int:id>', trainings.details, name="trainings-details"),
    path('<int:id>/anmelden', trainings.register, name="trainings-register"),
    path('<int:id>/abmelden', trainings.unregister,
         name="trainings-unregister"),
    path('erstellen', trainings.create, name="trainings-create"),
    path('<int:id>/bearbeiten', trainings.edit, name="trainings-edit"),
    path('<int:id>/entfernen', trainings.delete, name="trainings-delete")
]
