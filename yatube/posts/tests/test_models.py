from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            title='Тестовый заголовок',
            author=cls.user,
            text='Тестовый текст'
        )

    def test_models_have_correct_objects_name(self):
        """Проверяем что у моделей корректно работает __str__."""
        post = self.post
        self.assertEqual(post.text[:settings.TEXT_CROP], str(post))

        group = self.group
        self.assertEqual(group.title, str(group))

    def test_labels_have_correct_verbose_name(self):
        """Проверяем что verbose_name совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'title': 'Заголовок',
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_labels_have_correct_help_text(self):
        """Проверяем что help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_text = {
            'title': 'Введите название поста',
            'text': 'Текст нового поста',
            'author': 'Выберите автора поста из списка',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value
                )
