from django.contrib import auth
from django.test import TestCase, Client
from django.urls.base import reverse

from model_bakery import baker

from trainings.models import Training


class TestAccountUrls(TestCase):
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
        self.user.groups.add(
            auth.models.Group.objects.get_or_create(
                name='Administrator')[0].id
        )
        self.user.groups.add(
            auth.models.Group.objects.get_or_create(name='Trainer')[0].id)
        self.participants = baker.make('members.User', _quantity=5)
        self.trainings = baker.make(
            'trainings.Training', _quantity=10, make_m2m=True)
        self.c = Client()
        self.c.force_login(self.user)
        return super().setUp()

    def test_merge_search(self) -> None:
        self.assertEqual(16, auth.get_user_model().objects.count())
        response = self.c.get(reverse('members-merge'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/merge_search.html')

    def test_merge_detail(self) -> None:
        response = self.c.post(reverse('members-merge'),
                               {'users': ['1', '4']})
        self.assertRedirects(response, reverse('members-merge'))
        response = self.c.post(reverse('members-merge'),
                               {'users': ['1', '4'], 'action': 'detail'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/merge_users.html')

    def test_merge(self) -> None:
        user4 = auth.get_user_model().objects.get(id=4)
        user9 = auth.get_user_model().objects.get(id=9)
        email = user4.email
        last_name = user9.last_name
        training1 = self.trainings[0]
        training1.participants.add(user4.id)
        training1.registered_participants.add(user9.id)
        training2 = self.trainings[1]
        training2.participants.add(user4.id)
        training2.registered_participants.add(user4.id)
        training2.participants.add(user9.id)
        training2.registered_participants.add(user9.id)
        training3 = self.trainings[2]
        training3.visitors.add(user4.id)
        training3.instructors.add(user9.id)
        training4 = self.trainings[3]
        training4.coordinator = user4
        training4.save()
        training5 = self.trainings[4]
        training5.main_instructor = user9
        training5.save()
        self.assertNotEqual(
            email, auth.get_user_model().objects.get(id=1).email)
        self.assertNotEqual(
            last_name, auth.get_user_model().objects.get(id=1).last_name)
        response = self.c.post(reverse('members-merge'),
                               {
            'users': ['1', '4', '9'],
            'action': 'merge',
            'username': '1',
            'email': '4',
            'last_name': '9',
        }
        )
        self.assertEqual(email, auth.get_user_model().objects.get(id=1).email)
        self.assertEqual(
            last_name, auth.get_user_model().objects.get(id=1).last_name)
        self.assertEqual(14, auth.get_user_model().objects.count())
        self.assertRedirects(response, reverse('members-merge'))
        user = auth.get_user_model().objects.get(id=1)
        self.assertIn(user, training1.participants.all())
        self.assertIn(user, training1.registered_participants.all())
        self.assertIn(user, training2.participants.all())
        self.assertIn(user, training2.registered_participants.all())
        self.assertIn(user, training3.visitors.all())
        self.assertIn(user, training3.instructors.all())
        self.assertNotIn(user4, training1.participants.all())
        self.assertNotIn(user9, training1.registered_participants.all())
        self.assertNotIn(user4, training2.participants.all())
        self.assertNotIn(user4, training2.registered_participants.all())
        self.assertNotIn(user9, training2.participants.all())
        self.assertNotIn(user9, training2.registered_participants.all())
        self.assertNotIn(user4, training3.visitors.all())
        self.assertNotIn(user9, training3.instructors.all())
        training4 = Training.objects.get(id=training4.id)
        training5 = Training.objects.get(id=training5.id)
        self.assertEqual(user, training4.coordinator)
        self.assertEqual(user, training5.main_instructor)
