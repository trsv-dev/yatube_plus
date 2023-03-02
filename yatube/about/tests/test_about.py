from http import HTTPStatus

from django.conf import settings
from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/author/."""
        response = self.guest_client.get(settings.URL_ABOUT_AUTHOR)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/tech/."""
        response = self.guest_client.get(settings.URL_ABOUT_TECH)
        self.assertEqual(response.status_code, HTTPStatus.OK)
