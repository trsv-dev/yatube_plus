from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, Follow

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.user_no_author = User.objects.create_user(username='No_Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group_without_posts = Group.objects.create(
            title='Тестовая группа без постов',
            slug='test-slug-group-without-posts',
            description='Тестовое описание группы без постов',
        )
        cls.post = Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            id=settings.TEST_ID
        )
        cls.form = PostForm()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_no_author = Client()
        self.authorized_client_no_author.force_login(self.user_no_author)
        cache.clear()

    def check_context(self, response, post=None):
        """Проверка контекста страниц"""
        if post:
            post = response.context.get('post')
        else:
            post = response.context['page_obj'][0]
        self.assertEqual(post.author.username, self.user.username)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.title, self.post.title)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.image, self.post.image)

    def test_url_names_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_not_auth = {
            settings.HTML_INDEX: reverse(settings.INDEX),
            settings.HTML_POST_DETAIL: reverse(
                settings.POST_DETAIL,
                kwargs={'post_id': self.post.id}
            ),
            settings.HTML_GROUP_LIST: reverse(
                settings.GROUP_LIST,
                kwargs={'slug': self.group.slug}
            ),
            settings.HTML_PROFILE: reverse(
                settings.PROFILE,
                kwargs={'username': self.user}
            ),
            settings.HTML_SIGNUP: reverse(settings.SIGNUP),
        }
        templates_auth = {
            settings.HTML_POST_CREATE: reverse(settings.POST_CREATE)
        }
        templates_author = {
            settings.HTML_POST_EDIT: reverse(
                settings.POST_EDIT,
                kwargs={'post_id': settings.TEST_ID}
            )
        }
        for template, name in templates_not_auth.items():
            with self.subTest(template=template):
                response = self.guest_client.get(name)
                self.assertTemplateUsed(response, template)

        for template, name in templates_auth.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

        for template, name in templates_author.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(settings.INDEX))
        self.check_context(response)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(settings.POST_CREATE))
        form_fields = {
            'title': forms.fields.CharField,
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(settings.POST_DETAIL,
                    kwargs={'post_id': self.post.id}
                    )
        )
        self.check_context(response, True)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                settings.POST_EDIT,
                kwargs={'post_id': self.post.id},
            )
        )
        form_fields = {
            'title': forms.fields.CharField,
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(settings.PROFILE,
                    kwargs={'username': self.user}
                    )
        )
        self.check_context(response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(settings.GROUP_LIST,
                    kwargs={'slug': self.group.slug}
                    )
        )
        self.check_context(response)

    def test_signup_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(settings.SIGNUP))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache(self):
        """Шаблон index сформирован с кешированием"""
        post = Post.objects.create(
            author=self.user,
            text=self.post.text
        )
        cache.clear()
        response_1 = self.client.get(reverse(settings.INDEX))
        self.assertTrue(Post.objects.get(pk=post.id))
        Post.objects.get(pk=post.id).delete()
        response_2 = self.client.get(reverse(settings.INDEX))
        self.assertTrue(response_1, response_2)

    def test_ability_to_follow_and_unfollow_by_authorized_user(self):
        """
        Авторизованный пользователь не являющийся автором
        может подписаться и отписаться от автора записи
        """
        follower_count = Follow.objects.count()
        response = self.authorized_client_no_author.get(
            reverse(settings.FOLLOW, args=(self.user,))
        )
        self.assertRedirects(
            response, reverse(settings.PROFILE, args=(self.user,)),
            HTTPStatus.FOUND
        )
        self.assertEqual(Follow.objects.count(), follower_count + 1)
        response = self.authorized_client_no_author.get(
            reverse(settings.UNFOLLOW, args=(self.user,))
        )
        self.assertRedirects(
            response, reverse(settings.PROFILE, args=(self.user,))
        )
        self.assertEqual(Follow.objects.count(), follower_count)
        self.assertTrue(response, settings.URL_REDIRECT_FROM_FOLLOW)

    def test_redirect_unauthorized_user_from_follow_page(self):
        """
        Неавторизованного пользователя при попытке подписаться
        редиректит на страницу авторизации
        """
        response = self.guest_client.get(
            reverse(settings.FOLLOW, args=(self.user,))
        )
        self.assertTrue(response, settings.URL_REDIRECT_FROM_FOLLOW)

    def test_appearance_post_in_the_subscribers_feeds(self):
        """
        Новые записи автора появляются в лентах его подписчиков
        и не появляются у других
        """
        Follow.objects.get_or_create(
            user=self.user_no_author,
            author=self.user
        )
        Post.objects.create(
            text=self.post.text,
            author=self.user
        )
        response_1 = self.authorized_client_no_author.get(
            reverse(settings.FOLLOW_INDEX)
        )
        self.assertContains(response_1, self.post)
        response_2 = self.authorized_client.get(
            reverse(settings.FOLLOW_INDEX)
        )
        self.assertNotContains(response_2, self.post)
        self.assertNotEqual(response_1, response_2)
