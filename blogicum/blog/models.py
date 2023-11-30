from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()

MAX_STRING_LENGTH = 256
STR_LENGTH_LIMIT = 50


class PublishedCreatedModel(models.Model):
    """
    Абстрактная модель.
    Добавляет флаг is_published и время создания created_at.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(PublishedCreatedModel):
    """Модель категории."""

    title = models.CharField(
        max_length=MAX_STRING_LENGTH, verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:STR_LENGTH_LIMIT] + '...'


class Location(PublishedCreatedModel):
    """Модель геолокации."""

    name = models.CharField(
        max_length=MAX_STRING_LENGTH, verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:STR_LENGTH_LIMIT] + '...'


class Post(PublishedCreatedModel):
    """Модель публикации."""

    title = models.CharField(
        max_length=MAX_STRING_LENGTH, verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        verbose_name='Фото', blank=True, upload_to='post_images'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.title[:STR_LENGTH_LIMIT] + '...'

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={"post_id": self.pk})


class Comment(models.Model):
    """Модель комментария."""

    text = models.TextField(verbose_name='Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ['created_at']

    def __str__(self):
        return (
            'Комментарий к посту ' + self.post.title[:STR_LENGTH_LIMIT] + '...'
        )
