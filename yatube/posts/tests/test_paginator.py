from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post, User


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.ADDITIONAL_POSTS = settings.POSTS_PER_PAGE - 1
        cls.num_of_posts = (settings.POSTS_PER_PAGE
                            + cls.ADDITIONAL_POSTS)
        cls.posts_on_first_page = settings.POSTS_PER_PAGE
        cls.posts_on_second_page = (cls.num_of_posts
                                    - settings.POSTS_PER_PAGE)
        cls.list_of_test_posts = []
        for i in range(cls.num_of_posts):
            cls.list_of_test_posts.append(
                Post(
                    title=f'Тестовый заголовок поста No.{i}',
                    author=cls.user,
                    group=cls.group,
                    text=f'Тестовый текст No.{i}',
                    id=f'{i}'
                )
            )

        Post.objects.bulk_create(cls.list_of_test_posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_paginator_in_index_profile_group_list_pages(self):
        """
        Проверка работы паджинатора на первой и второй
        страницах: профиля, группы, главной
        """
        urls = {
            settings.INDEX: None,
            settings.GROUP_LIST: {'slug': self.group.slug},
            settings.PROFILE: {'username': self.user}
        }
        for url, data in urls.items():
            response1 = self.guest_client.get(
                reverse(url, kwargs=data)
            )
            response2 = self.guest_client.get(
                reverse(url, kwargs=data) + '?page=2'
            )
            self.assertEqual(len(response1.context['page_obj']),
                             self.posts_on_first_page)
            self.assertEqual(len(response2.context['page_obj']),
                             self.posts_on_second_page)
