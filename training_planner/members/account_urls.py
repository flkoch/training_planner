
from django.contrib.auth import views as auth_views
from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views as members

urlpatterns = [
    path('', members.account, name='account'),
    path(f'{_("login")}/', members.login, name='login'),
    path(f'{_("logout")}/', members.logout, name='logout'),
    path(f'{_("register")}/', members.register, name='register'),
    path(f'{_("edit")}/', members.account_edit, name='account-edit'),
    path(f'{_("password")}/{_("change")}/',
         auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path(f'{_("password")}/{_("change")}/{_("done")}/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path(f'{_("password")}/{_("reset")}/',
         auth_views.PasswordResetView.as_view(), name='password_reset'),
    path(f'{_("password")}/{_("reset")}/{_("done")}/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path(f'{_("password")}/{_("reset")}/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path(f'{_("password")}/{_("reset")}/{_("completed")}/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
