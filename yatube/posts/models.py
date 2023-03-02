from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название группы'
    )
    slug = models.SlugField(
        unique=True, max_length=100,
        verbose_name='Адрес группы (slug)',
        help_text='Введите адрес группы'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание группы'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name='Заголовок',
        help_text='Введите название поста'
    )
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    date_updated = models.DateTimeField(
        auto_now=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Выберите автора поста из списка'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    liked = models.ManyToManyField(
        User,
        default=None,
        blank=True,
        verbose_name='Лайкнули',
        related_name='liked_by',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:settings.TEXT_CROP]

    @property
    def num_likes(self):
        return self.liked.all().count()


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='comments',
        verbose_name='Запись',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка',
        verbose_name_plural = 'Подписки'


LIKE_CHOICES = (
    ('Нравится', 'Нравится'),
    ('Не нравится', 'Не нравится'),
)


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='liker'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='liking',
    )
    value = models.CharField(
        choices=LIKE_CHOICES,
        default='Нравится',
        max_length=11,
        verbose_name='Значение',
    )

    class Meta:
        verbose_name = 'Лайк',
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return str(self.post)


class BadWords(models.Model):
    word = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='"Плохие" слова',
        help_text='Введите новое фильтруемое слово'
    )

    class Meta:
        verbose_name = '"Плохое" слово',
        verbose_name_plural = '"Плохие" слова'

