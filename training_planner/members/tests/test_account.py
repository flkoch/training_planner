from django.contrib import auth
from django.test import TestCase, Client
from django.urls.base import reverse


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
        return super().setUp()

    def test_details_view(self) -> None:
        c = Client()
        c.force_login(self.user)
        response = c.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/details.html')
