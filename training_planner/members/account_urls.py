from django.contrib.auth import views as auth_views
from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views as members

urlpatterns = [
    path('', members.account, name='account'),
    path(_('login/'), members.login, name='login'),
    path(_('logout/'), members.logout, name='logout'),
    path(_('register/'), members.register, name='register'),
    path(_('edit/'), members.account_edit, name='account-edit'),
    path(_('password/change/'),
         auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path(_('password/change/done/'),
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path(_('password/reset/'),
         auth_views.PasswordResetView.as_view(), name='password_reset'),
    path(_('password/reset/done/'),
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path(_('password/reset/<uidb64>/<token>/'),
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path(_('password/reset/completed/'),
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
