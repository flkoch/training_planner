
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
    path(_('certificate/add/'), members.create_certificate,
         name='certificate-create'),
    path(_('<int:user_id>/certificate/add/'), members.create_certificate,
         name='certificate-create-id'),
    path(_('certificate/<int:id>/'), members.view_certificate,
         name='certificate-details'),
    path(_('certificate/<int:id>/edit/'), members.edit_certificate,
         name='certificate-edit'),
    path(_('certificate/<int:id>/delete/'), members.delete_certificate,
         name='certificate-delete'),
]
