from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.post = Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            id=settings.TEST_ID
        )

        cls.templates_not_auth = {
            settings.URL_INDEX: settings.HTML_INDEX,
            settings.URL_PROFILE: settings.HTML_PROFILE,
            settings.URL_POST_DETAIL: settings.HTML_POST_DETAIL,
            settings.URL_GROUP_LIST: settings.HTML_GROUP_LIST,
        }
        cls.templates_auth = {
            settings.URL_POST_CREATE: settings.HTML_POST_CREATE,
        }
        cls.templates_author = {
            settings.URL_POST_EDIT: settings.HTML_POST_EDIT,
        }
        cls.redirect_urls = {
            settings.URL_POST_CREATE: settings.URL_REDIRECT_FROM_CREATE,
            settings.URL_POST_EDIT: settings.URL_REDIRECT_FROM_EDIT
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_url_names_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for url, template in self.templates_not_auth.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

        for url, template in self.templates_auth.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

        for url, template in self.templates_author.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index(self):
        """Главная страница доступна"""
        response = self.guest_client.get(settings.URL_INDEX)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_author(self):
        """Страница редактирования поста доступна автору"""
        response = self.authorized_client.get(settings.URL_POST_EDIT)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_response_from_unexsisting_page(self):
        """Возврат ошибки 404 при переходе на несуществующую страницу."""
        response = self.guest_client.get(settings.URL_UNEXSISTING_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_for_non_author(self):
        """Страница редактирования поста не доступна не авторам"""
        self.user2 = User.objects.create_user(username='Not_Author')
        self.other_client = Client()
        self.other_client.force_login(self.user2)
        response = self.other_client.get(settings.URL_POST_EDIT)
        self.assertRedirects(response, settings.URL_REDIRECT_FOR_NOT_AUTHOR)
