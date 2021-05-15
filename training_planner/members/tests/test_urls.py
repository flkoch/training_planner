from django.contrib import auth
from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve

import members.views as views


class TestMembersURLs(SimpleTestCase):
    def test_members_all(self) -> None:
        url = reverse('members-all')
        self.assertEqual(resolve(url).func, views.all)

    def test_members_management(self) -> None:
        url = reverse('members-management')
        self.assertEqual(resolve(url).func, views.management)

    def test_members_merge(self) -> None:
        url = reverse('members-merge')
        self.assertEqual(resolve(url).func, views.merge)


class TestMemberURLs(TestCase):
    def setUp(self) -> None:
        self.userA = auth.get_user_model().objects.create_user(
            username='jane', email='jane@example.com', password='NoPassword'
        )
        return super().setUp()

    def test_members_details(self) -> None:
        url = reverse('member-details', args=[self.userA.id])
        self.assertEqual(resolve(url).func, views.details)

    def test_members_edit(self) -> None:
        url = reverse('member-edit', args=[self.userA.id])
        self.assertEqual(resolve(url).func, views.edit)


class TestAccountURLs(TestCase):
    def setUp(self) -> None:
        self.userA = auth.get_user_model().objects.create_user(
            username='jane', email='jane@example.com', password='NoPassword'
        )
        return super().setUp()

    def test_account_details(self) -> None:
        url = reverse('account')
        self.assertEqual(resolve(url).func, views.details)

    def test_account_edit(self) -> None:
        url = reverse('account-edit')
        self.assertEqual(resolve(url).func, views.edit)
