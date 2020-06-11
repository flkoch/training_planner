from django.test import SimpleTestCase
from django.urls import resolve, reverse

import trainings.views as views


class TestUrls(SimpleTestCase):
    def test_trainings_overview_url_resolves(self):
        url = reverse('trainings-overview')
        self.assertEquals(resolve(url).func, views.overview)

    def test_trainings_details_url_resolves(self):
        url = reverse('trainings-details', args=['3'])
        self.assertEquals(resolve(url).func, views.details)

    def test_trainings_register_url_resolves(self):
        url = reverse('trainings-register', args=[3])
        self.assertEquals(resolve(url).func, views.register)

    def test_trainings_unregister_url_resolves(self):
        url = reverse('trainings-unregister', args=[3])
        self.assertEquals(resolve(url).func, views.unregister)

    def test_trainings_register_coordinator_url_resolves(self):
        url = reverse('trainings-register-coordinator', args=[3])
        self.assertEquals(resolve(url).func, views.register_coordinator)

    def test_trainings_unregister_coordinator_url_resolves(self):
        url = reverse('trainings-unregister-coordinator', args=[3])
        self.assertEquals(resolve(url).func, views.unregister_coordinator)

    def test_trainings_create_url_resolves(self):
        url = reverse('trainings-create')
        self.assertEquals(resolve(url).func, views.create)

    def test_trainings_edit_url_resolves(self):
        url = reverse('trainings-edit', args=['3'])
        self.assertEquals(resolve(url).func, views.edit)

    def test_trainings_delete_url_resolves(self):
        url = reverse('trainings-delete', args=['3'])
        self.assertEquals(resolve(url).func, views.delete)

    def test_trainings_message_url_resolves(self):
        url = reverse('trainings-message', args=['3'])
        self.assertEquals(resolve(url).func, views.message)

    def test_trainings_series_url_resolves(self):
        url = reverse('trainings-series', args=['3'])
        self.assertEquals(resolve(url).func, views.make_series)

    def test_trainings_control_url_resolves(self):
        url = reverse('trainings-held')
        self.assertEquals(resolve(url).func, views.held)

    def test_trainings_controlling_url_resolves(self):
        url = reverse('trainings-controlling', args=['3'])
        self.assertEquals(resolve(url).func, views.controlling)

    def test_trainings_held_trainer_url_resolves(self):
        url = reverse('trainings-held-trainer', args=['3'])
        self.assertEquals(resolve(url).func, views.held)

    def test_trainings_participation_url_resolves(self):
        url = reverse('trainings-participation')
        self.assertEquals(resolve(url).func, views.participation)

    def test_trainings_all_url_resolves(self):
        url = reverse('trainings-management')
        self.assertEquals(resolve(url).func, views.management)
