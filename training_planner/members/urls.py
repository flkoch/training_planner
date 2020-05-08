
from django.urls import path
from . import views as members

urlpatterns = [
    path('', members.all, name='members-all'),
    path('<int:id>', members.details, name="member-details"),
    path('<int:id>/bearbeiten', members.edit, name="member-edit"),
]
