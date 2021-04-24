from django.contrib import auth, messages
from django.core import mail
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


from members import models as user


class TestUserRegistration(TestCase):
    def setUp(self) -> None:
        self.username = 'john'
        self.firstname = 'John'
        self.lastname = 'Doe'
        self.email = 'john@example.com'
        self.password = 'Th1s1sS3cur3'
        return super().setUp()

    def test_user_registration(self) -> None:
        c = Client()
        response = c.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        response = c.post(reverse('register'), {
            'username': self.username,  'password1': self.password,
            'password2': self.password, 'first_name': self.firstname,
            'last_name': self.lastname, 'email': self.email
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        user = auth.get_user_model().objects.get(username=self.username)
        self.assertEqual(user.last_name, self.lastname)
        self.assertEqual(user.first_name, self.firstname)
        self.assertEqual(user.email, self.email)
        message = str(list(messages.get_messages(response.wsgi_request))[0])
        self.assertEqual(
            message,
            _('The account has been created. '
              'Please check your inbox.')
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.email, mail.outbox[0].to)


class TestUserAuthentication(TestCase):
    def setUp(self) -> None:
        self.username = 'john'
        self.firstname = 'John'
        self.lastname = 'Doe'
        self.email = 'john@example.com'
        self.password = 'NoPassword'
        auth.get_user_model().objects.create_user(
            self.username,
            email=self.email,
            password=self.password,
            first_name=self.firstname,
            last_name=self.lastname,
        )
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        return super().setUp()

    def test_user_login_logout(self) -> None:
        c = Client()
        response = c.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(auth.get_user(c).is_authenticated)
        response = c.post(self.login_url, {
            'username': self.username, 'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(response.url, reverse('trainings-overview'))
        self.assertTrue(auth.get_user(c).is_authenticated)
        response = c.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(response.url, reverse('trainings-overview'))
        self.assertFalse(auth.get_user(c).is_authenticated)

    def test_user_login_wrong_pw(self) -> None:
        c = Client()
        response = c.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(auth.get_user(c).is_authenticated)
        response = c.post(self.login_url, {
            'username': self.username,
            'password': ''.join([self.password, 'wrong'])
        })
        self.assertFalse(auth.get_user(c).is_authenticated)
        response = c.post(self.login_url, {
            'username': self.username,
            'password': ''
        })
        self.assertFalse(auth.get_user(c).is_authenticated)


class TestUserPasswordChange(TestCase):
    def setUp(self) -> None:
        self.username = 'john'
        self.firstname = 'John'
        self.lastname = 'Doe'
        self.email = 'john@example.com'
        self.password = 'NoPassword'
        self.new_password = 'Secret&StrongP4ssw0rd'
        self.user = auth.get_user_model().objects.create_user(
            self.username,
            email=self.email,
            password=self.password,
            first_name=self.firstname,
            last_name=self.lastname,
        )
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.change_pw_url = reverse('password_change')
        return super().setUp()

    def test_password_change(self) -> None:
        c = Client()
        c.force_login(self.user)
        self.assertTrue(auth.get_user(c).is_authenticated)
        response = c.post(self.change_pw_url,
                          {
                              'old_password': self.password,
                              'new_password1': self.new_password,
                              'new_password2': self.new_password
                          })
        self.assertEqual(response.status_code, 302)
        response = c.get(self.logout_url)
        self.assertFalse(auth.get_user(c).is_authenticated)
        response = c.post(self.login_url, {
            'username': self.username, 'password': self.new_password
        })
        self.assertTrue(auth.get_user(c).is_authenticated)


class TestUserPasswordReset(TestCase):
    def setUp(self) -> None:
        self.username = 'john'
        self.firstname = 'John'
        self.lastname = 'Doe'
        self.email = 'john@example.com'
        self.password = 'NoPassword'
        auth.get_user_model().objects.create_user(
            self.username,
            email=self.email,
            password=self.password,
            first_name=self.firstname,
            last_name=self.lastname,
        )
        self.url = reverse('password_reset')
        return super().setUp()

    def test_password_reset(self) -> None:
        c = Client()
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = c.post(self.url, {'email': self.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.email, mail.outbox[0].to)

    def test_password_reset_unknown_address(self) -> None:
        c = Client()
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = c.post(self.url, {
            'email': ''.join(['unknown.', self.email])
        })
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_invalid_address(self) -> None:
        c = Client()
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = c.post(self.url, {
            'email': 'test'
        })
        self.assertRegexpMatches(response.content, b'<ul class="errorlist">')
        self.assertEqual(len(mail.outbox), 0)
        response = c.post(self.url, {
            'email': 'test#localhost'
        })
        self.assertRegexpMatches(response.content, b'<ul class="errorlist">')
        self.assertEqual(len(mail.outbox), 0)


class TestUserMethods(TestCase):
    def setUp(self) -> None:
        self.username = 'john'
        self.firstname = 'John'
        self.lastname = 'Doe'
        self.email = 'john@example.com'
        self.password = 'NoPassword'
        self.user = auth.get_user_model().objects.create_user(
            self.username,
            email=self.email,
            password=self.password,
            first_name=self.firstname,
            last_name=self.lastname,
        )
        return super().setUp()

    def test_user_initials(self) -> None:
        initials = self.user.get_initials()
        self.assertEqual(
            initials,
            ''.join([self.firstname[0], self.lastname[0]])
        )
        paran_init = self.user.get_initials_paranthesised()
        self.assertEqual(paran_init, initials.join(['(', ')']))

    def test_user_public_name(self) -> None:
        pub_name = self.user.get_public_name()
        self.assertEqual(pub_name,
                         ''.join([self.firstname, ' ', self.lastname[0], '.']))

    def test_user_name(self) -> None:
        self.assertEqual(
            self.user.name,
            ' '.join([self.firstname, self.lastname])
        )

    def test_user_name_or_username(self) -> None:
        self.assertEqual(self.user.name_or_username, self.user.get_full_name())
        self.user.first_name = ''
        self.user.save()
        self.assertEqual(self.user.name_or_username, self.username)
        self.user.first_name = self.firstname
        self.user.save()

    def test_user_group_properties(self) -> None:
        self.assertFalse(self.user.is_trainer)
        self.assertFalse(self.user.is_active_trainer)
        self.assertFalse(self.user.is_participant)
        self.assertFalse(self.user.is_active_participant)
        self.assertFalse(self.user.is_administrator)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Trainer'))
        self.user.save()
        self.assertTrue(self.user.is_trainer)
        self.assertFalse(self.user.is_active_trainer)
        self.assertFalse(self.user.is_participant)
        self.assertFalse(self.user.is_active_participant)
        self.assertFalse(self.user.is_administrator)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Active Trainer'))
        self.user.save()
        self.assertTrue(self.user.is_trainer)
        self.assertTrue(self.user.is_active_trainer)
        self.assertFalse(self.user.is_participant)
        self.assertFalse(self.user.is_active_participant)
        self.assertFalse(self.user.is_administrator)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Participant'))
        self.user.save()
        self.assertTrue(self.user.is_trainer)
        self.assertTrue(self.user.is_active_trainer)
        self.assertTrue(self.user.is_participant)
        self.assertFalse(self.user.is_active_participant)
        self.assertFalse(self.user.is_administrator)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Active Participant'))
        self.user.save()
        self.assertTrue(self.user.is_trainer)
        self.assertTrue(self.user.is_active_trainer)
        self.assertTrue(self.user.is_participant)
        self.assertTrue(self.user.is_active_participant)
        self.assertFalse(self.user.is_administrator)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Administrator'))
        self.user.save()
        self.assertTrue(self.user.is_trainer)
        self.assertTrue(self.user.is_active_trainer)
        self.assertTrue(self.user.is_participant)
        self.assertTrue(self.user.is_active_participant)
        self.assertTrue(self.user.is_administrator)
        self.user.groups.clear()
        self.user.save()
        self.assertFalse(self.user.is_trainer)
        self.assertFalse(self.user.is_active_trainer)
        self.assertFalse(self.user.is_participant)
        self.assertFalse(self.user.is_active_participant)
        self.assertFalse(self.user.is_administrator)

    def test_user_group_retrieval(self) -> None:
        self.assertEqual(len(user.all()), 1)
        self.assertEqual(len(user.active_participant()), 0)
        self.assertEqual(len(user.participant()), 0)
        self.assertEqual(len(user.active_trainer()), 0)
        self.assertEqual(len(user.trainer()), 0)
        self.assertEqual(len(user.administrator()), 0)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Trainer'))
        self.user.save()
        self.assertEqual(len(user.all()), 1)
        self.assertEqual(len(user.active_participant()), 0)
        self.assertEqual(len(user.participant()), 0)
        self.assertEqual(len(user.active_trainer()), 0)
        self.assertEqual(len(user.trainer()), 1)
        self.assertEqual(len(user.administrator()), 0)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Active Trainer'))
        self.user.save()
        self.assertEqual(len(user.all()), 1)
        self.assertEqual(len(user.active_participant()), 0)
        self.assertEqual(len(user.participant()), 0)
        self.assertEqual(len(user.active_trainer()), 1)
        self.assertEqual(len(user.trainer()), 1)
        self.assertEqual(len(user.administrator()), 0)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Participant'))
        self.user.save()
        self.assertEqual(len(user.all()), 1)
        self.assertEqual(len(user.active_participant()), 0)
        self.assertEqual(len(user.participant()), 1)
        self.assertEqual(len(user.active_trainer()), 1)
        self.assertEqual(len(user.trainer()), 1)
        self.assertEqual(len(user.administrator()), 0)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Active Participant'))
        self.user.save()
        self.assertEqual(len(user.all()), 1)
        self.assertEqual(len(user.active_participant()), 1)
        self.assertEqual(len(user.participant()), 1)
        self.assertEqual(len(user.active_trainer()), 1)
        self.assertEqual(len(user.trainer()), 1)
        self.assertEqual(len(user.administrator()), 0)
        self.user.groups.add(get_object_or_404(
            auth.models.Group, name='Administrator'))
        self.user.save()
        self.assertEqual(len(user.all()), 1)
        self.assertEqual(len(user.active_participant()), 1)
        self.assertEqual(len(user.participant()), 1)
        self.assertEqual(len(user.active_trainer()), 1)
        self.assertEqual(len(user.trainer()), 1)
        self.assertEqual(len(user.administrator()), 1)
        self.user.groups.clear()
        self.user.save()
        self.assertEqual(len(user.all()), 1)
        self.assertEqual(len(user.active_participant()), 0)
        self.assertEqual(len(user.participant()), 0)
        self.assertEqual(len(user.active_trainer()), 0)
        self.assertEqual(len(user.trainer()), 0)
        self.assertEqual(len(user.administrator()), 0)
