from django.urls import path
from . import views as trainings

urlpatterns = [
    path('', trainings.overview, name="trainings-overview")
]
