import math
import random

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import trainings.models as models

User = get_user_model()


class TestViewsNoData(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.login_url = reverse('login')
        self.overview_url = reverse('trainings-overview')
        self.create_url = reverse('trainings-create')
        self.control_url = reverse('trainings-held')
        self.participation_url = reverse('trainings-participation')
        self.all_url = reverse('trainings-all')
        self.management_url = reverse('trainings-management')

    def test_trainings_overview_GET(self) -> None:
        response = self.client.get(self.overview_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trainings/overview.html')

    def test_trainings_create_GET(self) -> None:
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_trainings_create_POST(self) -> None:
        response = self.client.post(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_trainings_control_GET(self) -> None:
        response = self.client.get(self.control_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_trainings_participation_GET(self) -> None:
        response = self.client.get(self.participation_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_trainings_all_GET(self) -> None:
        response = self.client.get(self.all_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_training_management_GET(self) -> None:
        response = self.client.get(self.management_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)


class TestViewsAnonymous(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.trainer = User.objects.create_user(
            username='test_trainer',
            password='test_password',
        )
        self.target_groups = [
            models.TargetGroup.objects.create(name='Group ' + str(i + 1))
            for i in range(4)
        ]
        self.trainings = [
            models.Training.objects.create(
                title='Title ' + str(i + 1),
                start=timezone.now() - timezone.timedelta(days=i),
                duration=60,
                main_instructor=self.trainer,
                registration_open=timezone.now(),
                registration_close=timezone.now(),
            )
            for i in range(10)
        ]
        for training in self.trainings:
            training.target_group.set([
                self.target_groups[math.floor(random.random() * 4)]
            ])
            training.set_registration_times(21, 1)
        self.login_url = reverse('login')
        self.overview_url = reverse('trainings-overview')
        self.all_url = reverse('trainings-all')
        self.detail_url = [reverse('trainings-details', args=[i + 1])
                           for i in range(10)]

    def test_training_details_GET(self) -> None:
        response = self.client.get(self.detail_url[2])
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)


class TestViewsParticipant(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.participant_group = Group.objects.get(name='Participant')
        self.participant = User.objects.create_user(
            username='test_participant',
            password='test_password',
        )
        self.participant_group.user_set.add(self.participant)
        self.trainer = User.objects.create_user(
            username='test_trainer',
            password='test_password',
        )
        self.target_groups = [
            models.TargetGroup.objects.create(name='Group ' + str(i + 1))
            for i in range(4)
        ]
        self.trainings = [
            models.Training.objects.create(
                title='Title ' + str(i + 1),
                start=timezone.now() - timezone.timedelta(days=i),
                duration=60,
                main_instructor=self.trainer,
                registration_open=timezone.now(),
                registration_close=timezone.now(),
            )
            for i in range(10)
        ]
        for training in self.trainings:
            training.target_group.set([
                self.target_groups[math.floor(random.random() * 4)]
            ])
            training.set_registration_times(21, 1)
        self.login_url = reverse('login')
        self.overview_url = reverse('trainings-overview')
        self.all_url = reverse('trainings-all')
        self.detail_url = [reverse('trainings-details', args=[i + 1])
                           for i in range(10)]

    def test_training_all_GET_participant(self) -> None:
        self.client.force_login(self.participant)
        response = self.client.get(self.all_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.overview_url)

    def test_training_details_GET_participant(self) -> None:
        self.client.force_login(self.participant)
        response = self.client.get(self.detail_url[2])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trainings/details.html')


class TestViewsTrainer(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.trainer_group = Group.objects.get(name='Trainer')
        self.trainer1 = User.objects.create_user(
            username='test_trainer1',
            password='test_password',
        )
        self.trainer_group.user_set.add(self.trainer1)
        self.trainer2 = User.objects.create_user(
            username='test_trainer2',
            password='test_password',
        )
        self.trainer_group.user_set.add(self.trainer2)
        self.target_groups = [
            models.TargetGroup.objects.create(name='Group ' + str(i + 1))
            for i in range(4)
        ]
        self.trainings = [
            models.Training.objects.create(
                title='Title ' + str(i + 1),
                start=timezone.now() - timezone.timedelta(days=i),
                duration=60,
                main_instructor=(
                    self.trainer1 if i // 2 == 0 else self.trainer2
                ),
                registration_open=timezone.now(),
                registration_close=timezone.now(),
            )
            for i in range(10)
        ]
        for training in self.trainings:
            training.target_group.set([
                self.target_groups[math.floor(random.random() * 4)]
            ])
            training.set_registration_times(21, 1)
        self.login_url = reverse('login')
        self.overview_url = reverse('trainings-overview')
        self.all_url = reverse('trainings-all')
        self.detail_url = [reverse('trainings-details', args=[i + 1])
                           for i in range(10)]

    def test_training_all_GET_trainer(self) -> None:
        self.client.force_login(self.trainer1)
        response = self.client.get(self.all_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trainings/overview.html')

    def test_training_details_GET_trainer(self) -> None:
        self.client.force_login(self.trainer1)
        response = self.client.get(self.detail_url[2])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trainings/details_admin.html')


class TestViewsAdministrator(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.trainer_group = Group.objects.get(name='Trainer')
        self.admin_group = Group.objects.get(name='Administrator')
        self.trainer = User.objects.create_user(
            username='test_trainer',
            password='test_password',
        )
        self.trainer_group.user_set.add(self.trainer)
        self.admin = User.objects.create_user(
            username='test_admin',
            password='test_password',
        )
        self.admin_group.user_set.add(self.admin)
        self.client.force_login(self.admin)
        self.target_groups = [
            models.TargetGroup.objects.create(name='Group ' + str(i + 1))
            for i in range(4)
        ]
        self.trainings = [
            models.Training.objects.create(
                title='Title ' + str(i + 1),
                start=timezone.now() - timezone.timedelta(days=i),
                duration=60,
                main_instructor=self.trainer,
                registration_open=timezone.now(),
                registration_close=timezone.now(),
            )
            for i in range(10)
        ]
        for training in self.trainings:
            training.target_group.set([
                self.target_groups[math.floor(random.random() * 4)]
            ])
            training.set_registration_times(21, 1)
        self.overview_url = reverse('trainings-overview')
        self.detail_url = [reverse('trainings-details', args=[i + 1])
                           for i in range(10)]
        self.register_participant_url = [
            reverse('trainings-register-participant', args=[i + 1])
            for i in range(10)
        ]
        self.unregister_participant_url = [
            reverse('trainings-unregister-participant', args=[i + 1])
            for i in range(10)
        ]
        self.register_visitor_url = [
            reverse('trainings-register-visitor', args=[i + 1])
            for i in range(10)
        ]
        self.unregister_visitor_url = [
            reverse('trainings-unregister-visitor', args=[i + 1])
            for i in range(10)
        ]
        self.register_coordinator_url = [
            reverse('trainings-register-coordinator', args=[i + 1])
            for i in range(10)
        ]
        self.unregister_coordinator_url = [
            reverse('trainings-unregister-coordinator', args=[i + 1])
            for i in range(10)
        ]
        self.create_url = reverse('trainings-create')
        self.edit_url = [reverse('trainings-edit', args=[i + 1])
                         for i in range(10)]
        self.delete_url = [reverse('trainings-delete', args=[i + 1])
                           for i in range(10)]
        self.message_url = [reverse('trainings-message', args=[i + 1])
                            for i in range(10)]
        self.series_url = [reverse('trainings-series', args=[i + 1])
                           for i in range(10)]
        self.control_url = reverse('trainings-held')
        self.controlling_url = [reverse('trainings-controlling', args=[i + 1])
                                for i in range(10)]
        self.trainings_held_trainer_url = reverse(
            'trainings-held-trainer',
            args=[self.trainer.id]
        )
        self.participation_url = reverse('trainings-participation')
        self.management_url = reverse('trainings-management')
        self.all_url = reverse('trainings-all')

    def test_training_overview(self) -> None:
        response = self.client.get(self.overview_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trainings/overview.html')

    def test_training_details_GET_administrator(self) -> None:
        responses = [self.client.get(self.detail_url[i]) for i in range(10)]
        for response in responses:
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'trainings/details_admin.html')

    def test_training_register_participant_GET_administrator(self) -> None:
        responses = [self.client.get(self.register_participant_url[i])
                     for i in range(10)]
        for i, response in enumerate(responses):
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.detail_url[i])
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(str(messages[0]), _('Registration failed.'))

    def test_training_unregister_participant_GET_administrator(self) -> None:
        responses = [self.client.get(self.unregister_participant_url[i])
                     for i in range(10)]
        for i, response in enumerate(responses):
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.overview_url)
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(str(messages[0]), _('Sign-off failed.'))

    def test_training_register_visitor_GET_administrator(self) -> None:
        responses = [self.client.get(self.register_visitor_url[i])
                     for i in range(10)]
        for i, response in enumerate(responses):
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.detail_url[i])
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(str(messages[0]), _('Registration failed.'))

    def test_training_unregister_visitor_GET_administrator(self) -> None:
        responses = [self.client.get(self.unregister_visitor_url[i])
                     for i in range(10)]
        for i, response in enumerate(responses):
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.overview_url)
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(str(messages[0]), _('Sign-off failed.'))

    def test_training_all_GET_administrator(self) -> None:
        response = self.client.get(self.all_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trainings/overview.html')
