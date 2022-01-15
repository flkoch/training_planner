from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import decorators as auth_decorators
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from trainings import decorators

from .filter import UserFilter
from .forms import (CertificateForm, ChangeUserForm, CreateCertificateForm,
                    CreateUserForm)
from .models import (Certificate, User, check_active_participants,
                     check_active_trainers, check_trainers)

# Create your views here.


@decorators.unauthorised_user
def login(request):
    username = ''
    if request.method == 'POST':
        user = auth.authenticate(request,
                                 username=request.POST.get('username'),
                                 password=request.POST.get('password'))
        if user is not None:
            auth.login(request, user)
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('trainings-overview')
        else:
            messages.info(
                request,
                _('Username and password do not match a valid user.')
            )
    context = {'username': username}
    return render(request, 'members/login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('trainings-overview')


@decorators.unauthorised_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not (user.initials and user.initials.strip()):
                user.initials = user.get_initials()
            user.save()
            user.groups.add(get_object_or_404(
                auth.models.Group, name='Participant'))
            form.save_m2m()
            subject = format_lazy(
                _('Registration on {website}'),
                website=settings.ALLOWED_HOSTS[0] if len(
                    settings.ALLOWED_HOSTS) > 0 else 'TrainingPlanner'
            )
            message = format_lazy(
                _(
                    'Hi {name},\nWe are happy to have you on our '
                    'platform, which allows you to register for and '
                    'participate in offered training sessions.\nIf you have '
                    'questions on the requirements for participation contact '
                    'the instructor or the administration.\nFor each Training '
                    'we need a coordinator. If you could do this from time to '
                    'time everyone will enjoy the experience.\nEnjoy your '
                    'trainings\nYour Instructor team'
                ),
                name=user.first_name
            )
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.send()
            messages.success(
                request,
                _('The account has been created. '
                  'Please check your inbox.')
            )
            return redirect(login)
    context = {
        'title': _('Register'),
        'form': form,
    }
    return render(request, 'members/user_form.html', context)


@auth_decorators.permission_required('members.view_user')
def all(request):
    users = User.objects.all().exclude(groups__name='System') \
        .order_by('last_name', 'first_name')
    myFilter = UserFilter(request.GET, queryset=users)
    users = myFilter.qs
    context = {'users': users, 'myFilter': myFilter}
    return render(request, 'members/overview.html', context)


@auth_decorators.login_required
def details(request, id=None):
    show_cert = request.user.has_perm('members.view_certificate')
    certs = None
    if id is None:
        user = request.user
        edit_link = reverse('account-edit')
        show_cert = True
    else:
        user = get_object_or_404(auth.get_user_model(), id=id)
        if user == request.user:
            return redirect('account')
        elif not request.user.has_perm('members.view_user'):
            messages.info(
                request,
                _('Only trainers and administrators may access this area.')
            )
            return redirect('trainings-overview')
        edit_link = reverse('member-edit', args=[id])
    reg_trainings = user.trainings_registered.filter(
        start__gte=timezone.now()).order_by('start')
    part_trainings = user.trainings.filter(
        start__lte=timezone.now()).order_by('-start')
    visited_trainings = user.visited_trainings.all()
    paginator = Paginator(part_trainings, 10)
    page_number = request.GET.get('page1')
    page_obj1 = paginator.get_page((page_number))
    paginator = Paginator(visited_trainings, 10)
    page_number = request.GET.get('page2')
    page_obj2 = paginator.get_page((page_number))
    if show_cert:
        certs = user.certificates.filter(
            date_end__gte=timezone.now()).order_by('date_end')
    context = {
        'page_user': user,
        'edit_link': edit_link,
        'reg_trainings': reg_trainings,
        'part_trainings': page_obj1,
        'visited_trainings': page_obj2,
        'show_certs': show_cert,
        'certs': certs,
    }
    return render(request, 'members/details.html', context)


@auth_decorators.login_required
def edit(request, id=None):
    if id is None:
        user = request.user
    else:
        user = get_object_or_404(auth.get_user_model(), id=id)
        if user == request.user:
            return redirect('account-edit')
        elif not request.user.has_perm('members.edit'):
            messages.info(
                request,
                _('Only trainers and administrators may access this area.')
            )
            return redirect('trainings-overview')
    if request.method == 'POST':
        form = ChangeUserForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.initials = ''.join(
                c for c in form.cleaned_data['initials'] if c.isalpha()
            ).upper()
            user.birth_date = form.cleaned_data['birth_date']
            user.save()
            if id is None:
                return redirect('account')
            else:
                return redirect('member-details', id=id)
    form = ChangeUserForm(instance=user)
    context = {
        'title': _('Edit User'),
        'form': form,
    }
    return render(request, 'members/user_form.html', context)


@auth_decorators.login_required
@decorators.admin_only
def management(request):
    if request.method == 'POST':
        print(request.POST)
        if 'check_active_participants' in request.POST:
            check_active_participants(weeks=15)
            messages.success(request, _('Update Active Participants'))
        elif 'check_active_trainers' in request.POST:
            check_active_trainers(weeks=15)
            messages.success(request, _('Update Active Trainer'))
        elif 'check_trainers' in request.POST:
            check_trainers(weeks=15)
            messages.success(request, _('Update Trainer'))
    return render(request, 'members/user_management.html')


@auth_decorators.login_required
@decorators.admin_only
@csrf_protect
def merge(request):
    if request.method != 'POST':
        users = User.objects.all().exclude(groups__name='System') \
            .order_by('last_name', 'first_name')
        myFilter = UserFilter(request.GET, queryset=users)
        users = myFilter.qs
        context = {'users': users, 'myFilter': myFilter}
        return render(request, 'members/merge_search.html', context)
    user_ids = request.POST.getlist('users')
    users = User.objects.filter(id__in=user_ids).order_by(
        '-id').order_by('-last_login')
    if request.POST.get('action') == 'detail':
        if len(users) < 2:
            messages.error(
                request,
                _('For merging you need to select at least two users.')
            )
            return redirect('members-merge')
        context = {'users': users}
        return render(request, 'members/merge_users.html', context)
    if request.POST.get('action') == 'merge':
        username_id = request.POST.get('username')
        first_name_id = request.POST.get('first_name')
        last_name_id = request.POST.get('last_name')
        birth_date_id = request.POST.get('birth_date')
        email_id = request.POST.get('email')
        initials_id = request.POST.get('initials')
        main_user = users.get(id=username_id)
        if first_name_id is not None and first_name_id != username_id:
            main_user.first_name = users.get(id=first_name_id).first_name
        if last_name_id is not None and last_name_id != username_id:
            main_user.last_name = users.get(id=last_name_id).last_name
        if birth_date_id is not None and birth_date_id != username_id:
            main_user.birth_date = users.get(id=birth_date_id).birth_date
        if email_id is not None and email_id != username_id:
            main_user.email = users.get(id=email_id).email
        if initials_id is not None and initials_id != username_id:
            main_user.initials = users.get(id=initials_id).initials
        main_user.save()
        other_users = users.exclude(id=username_id)
        for user in other_users:
            for training in user.instructor.all():
                training.main_instructor = main_user
                training.save()
            for training in user.assistant.all():
                training.instructors.add(main_user.id)
                training.instructors.remove(user.id)
            for training in user.coordinated_trainings.all():
                training.coordinator = main_user
                training.save()
            for training in user.trainings_registered.all():
                training.registered_participants.add(main_user.id)
                training.registered_participants.remove(user.id)
            for training in user.trainings.all():
                training.participants.add(main_user.id)
                training.participants.remove(user.id)
            for training in user.visited_trainings.all():
                training.visitors.add(main_user.id)
                training.visitors.remove(user.id)
            for group in user.groups.all():
                main_user.groups.add(group)
            for cert in user.certificates.all():
                cert.user = main_user
                cert.save()
        messages.success(
            request,
            _('The users were merged and additional accounts were deleted.')
        )
        other_users.delete()
    return redirect('members-merge')


@auth_decorators.login_required
def view_certificate(request, id=None):
    if id is None:
        return redirect('certificates-all')
    certificate = get_object_or_404(Certificate, id=id)
    valid = certificate.is_valid
    can_edit = False
    can_delete = False
    if request.user.has_perm('members.edit_certificate'):
        can_edit = True
    if request.user.has_perm('members.delete_certificate'):
        can_delete = True
    res_full = certificate.restrictions_fulfilled.all()
    res_part = certificate.restrictions_part_fulfilled.all()
    context = {'certificate': certificate,
               'res_full': res_full, 'res_part': res_part, 'valid': valid,
               'can_edit': can_edit, 'can_delete': can_delete}
    return render(request, 'members/certificate.html', context)


@auth_decorators.login_required
@auth_decorators.permission_required('members.create_certificate')
def create_certificate(request, user_id=None):
    if request.method == 'POST':
        form = CreateCertificateForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=True)
            messages.success(request, _('Certificate added successfully.'))
            return redirect('certificate-details', cert.id)
        else:
            messages.warning(
                request,
                _('Please take care of the highlighted errors.')
            )
    else:
        if user_id is None:
            user = None
        else:
            user = get_object_or_404(auth.get_user_model(), id=user_id)
        form = CertificateForm(
            initial={
                'user': user,
                'date_start': timezone.now().date()
            }
        )
    context = {'form': form, 'title': _('New Certificate')}
    return render(request, 'members/certificate_form.html', context)


@auth_decorators.login_required
@auth_decorators.permission_required('members.edit_certificate')
def edit_certificate(request, id):
    cert = get_object_or_404(Certificate, id=id)
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=True)
            messages.success(request, _('Certificate added successfully.'))
            return redirect('certificate-details', cert.id)
        else:
            messages.warning(
                request,
                _('Please take care of the highlighted errors.')
            )
    else:
        form = CertificateForm(instance=cert)
    title = _('Certificate')
    context = {'form': form, 'user': cert.user,
               'title': title}
    return render(request, 'members/certificate_form.html', context)


@auth_decorators.login_required
@auth_decorators.permission_required('members.delete_certificate')
def delete_certificate(request, id):
    cert = get_object_or_404(Certificate, id=id)
    if request.method == 'POST' and \
            request.POST['_method'] == 'delete' and \
            request.POST['id'] == str(id):
        user_id = cert.user.id
        cert.delete()
        messages.success(
            request,
            _('The certificate was successfully deleted.')
        )
        return redirect('member-details', user_id)
    context = {'obj': cert, 'title': _('Certificate')}
    return render(request, 'members/delete.html', context)
