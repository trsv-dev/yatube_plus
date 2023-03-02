from django.test import TestCase, Client
from http import HTTPStatus
from django.conf import settings


class ViewTestClass(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_error_404_page(self):
        """Страница 404 использует соответствующий шаблон"""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, settings.HTML_404)
