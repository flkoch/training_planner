
from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views as members

urlpatterns = [
    path('', members.all, name='members-all'),
    path(_('management/'),
         members.management, name='members-management'),
    path(_('merge'), members.merge, name='members-merge'),
    path('<int:id>/', members.details, name='member-details'),
    path(_('<int:id>/edit/'), members.edit, name='member-edit'),
]
