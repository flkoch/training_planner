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
from django.urls import path, include
from django.contrib.auth import views as auth_views

from website.views import welcome
from members.views import login, logout, account, register

urlpatterns = [
    path('', welcome, name='home'),
    path('login', login, name='login'),
    path('logout', logout, name='logout'),
    path('register', register, name='register'),
    path('account', account, name='account'),
    path('account/reset-password',
         auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('account/reset-password-done',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('account/reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('account/password-complete',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('mitglieder/', include('members.urls')),
    path('trainings/', include('trainings.urls')),
    path('admin/', admin.site.urls),
]
