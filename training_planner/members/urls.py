
from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views as members

urlpatterns = [
    path('', members.all, name='members-all'),
    path(f'{_("management/")}',
         members.user_management, name='user-management'),
    path('<int:id>/', members.details, name='member-details'),
    path(f'<int:id>/{_("edit")}/', members.edit, name='member-edit'),
]
