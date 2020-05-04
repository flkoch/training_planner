from django.urls import path
from . import views as trainings

urlpatterns = [
    path('', trainings.overview, name="trainings-overview"),
    path('<int:id>', trainings.details, name="trainings-details"),
    path('erstellen', trainings.create, name="trainings-create"),
    path('bearbeiten/<int:id>', trainings.edit, name="trainings-edit"),
    path('entfernen/<int:id>', trainings.delete, name="trainings-delete")
]
