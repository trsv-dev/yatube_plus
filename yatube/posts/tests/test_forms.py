import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group_without_posts = Group.objects.create(
            title='Тестовая группа без постов',
            slug='test-slug-group-without-posts',
            description='Тестовое описание группы без постов'
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_user_create_post_with_image(self):
        """
        Валидная форма от авторизованного пользователя создает
        пост с изображением.
        """
        posts_count = Post.objects.count()
        form_data = {
            'title': self.post.title,
            'author': self.authorized_client,
            'group': self.group.id,
            'text': self.post.text,
            'image': self.image,
        }
        response = self.authorized_client.post(
            reverse(settings.POST_CREATE),
            form_data, follow=True
        )
        self.assertRedirects(
            response, reverse(
                settings.PROFILE, kwargs={'username': self.user}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                title=self.post.title,
                text=self.post.text,
                group=self.post.group,
                image=self.post.image
            ).exists()
        )

    def test_new_post_from_authorized_user(self):
        """Создается новая запись в базе данных"""
        posts_count = Post.objects.count()
        form_data = {
            'title': self.post.title,
            'text': self.post.text,
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse(settings.POST_CREATE),
            form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text=self.post.text).exists()
        )

    def test_change_text_post_from_authorized_user(self):
        """Происходит изменение поста в базе данных"""
        form_data = {
            'title': self.post.title,
            'text': 'Измененный тестовый текст',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse(settings.POST_EDIT,
                    kwargs={'post_id': self.post.id}),
            form_data, follow=True
        )
        response = self.authorized_client.get(
            reverse(settings.POST_DETAIL,
                    kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'].text,
                         form_data['text'])

    def test_change_group_post_from_authorized_user(self):
        """Происходит изменение группы в базе данных"""
        form_data = {
            'title': self.post.title,
            'text': 'Измененный тестовый текст',
            'group': self.group_without_posts.id,
        }
        self.authorized_client.post(
            reverse(settings.POST_EDIT,
                    kwargs={'post_id': self.post.id}),
            form_data, follow=True
        )
        self.authorized_client.get(
            reverse(settings.POST_DETAIL,
                    kwargs={'post_id': self.post.id}))
        self.assertTrue(
            Post.objects.filter(
                title=self.post.title,
                text='Измененный тестовый текст',
                group=self.group_without_posts.id,
                author=self.user
            ).exists()
        )

    def test_creating_user_if_form_is_filled_correctly(self):
        """
        Создается новый пользователь если форма
        регистрации заполнена верно
        """
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'username': 'Test2Test',
            'email': 'test2test@test.test',
            'password1': '1234Rty7890_!',
            'password2': '1234Rty7890_!'
        }
        response = self.guest_client.post(
            reverse(settings.SIGNUP),
            form_data, follow=True
        )
        user = User.objects.last()
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.last_name, form_data['last_name'])
        self.assertEqual(user.username, form_data['username'])
        self.assertRedirects(response, reverse(settings.INDEX))
        self.assertEqual(User.objects.count(), users_count + 1)

    def test_create_comment_from_authorized_user(self):
        """
        Комментировать записи могут только
        авторизованные пользователи
        """
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse(settings.ADD_COMMENT,
                    kwargs={'post_id': self.post.id}),
            form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(text=form_data['text']).exists()
        )
        last_comment = Comment.objects.last().text
        self.assertEqual(last_comment, form_data['text'])
        self.assertRedirects(
            response, reverse(
                settings.POST_DETAIL, kwargs={'post_id': self.post.id}
            )
        )

    def test_create_comment_from_unauthorized_user(self):
        """
        Неавторизованные пользователи не могут
        комментировать записи
        """
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Анонимный тестовый комментарий',
        }
        response = self.guest_client.post(
            reverse(settings.ADD_COMMENT,
                    kwargs={'post_id': self.post.id}),
            form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertTrue(response, settings.URL_REDIRECT_FROM_COMMENT)
