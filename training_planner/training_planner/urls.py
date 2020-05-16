"""training_planner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.utils.translation import gettext as _

from website.views import welcome
from members.views import login, logout, account, account_edit, register

urlpatterns = [
    path('', welcome, name='home'),
    path(_('login'), login, name='login'),
    path(_('logout'), logout, name='logout'),
    path(_('register'), register, name='register'),
    path(_('konto/'), account, name='account'),
    path(_('konto/bearbeiten'), account_edit, name='account-edit'),
    path(_('konto/passwort-reset'),
         auth_views.PasswordResetView.as_view(), name='reset_password'),
    path(_('konto/passwort-reset-initiiert'),
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path(_('konto/reset/<uidb64>/<token>'),
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path(_('konto/passwort-angepasst'),
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path(_('mitglieder/'), include('members.urls')),
    path(_('trainings/'), include('trainings.urls')),
    path('admin/', admin.site.urls),
]
