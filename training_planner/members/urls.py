
from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views as members

urlpatterns = [
    path('', members.all, name='members-all'),
    path(_('verwaltung'), members.user_management, name='user-management'),
    path('<int:id>', members.details, name='member-details'),
    path(_('<int:id>/bearbeiten'), members.edit, name='member-edit'),
]
