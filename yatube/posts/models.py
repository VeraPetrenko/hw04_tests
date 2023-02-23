from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор поста',
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите картинку'
    )
    comment = models.ForeignKey(
        'Comment',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Комментарии',
        help_text='Комментарии к посту',
        related_name='posts'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка'
    )
    description = models.TextField(
        verbose_name='Описание группы'
    )

    # Чтобы не перегружать админку,
    # ограничиваем вывод title 30 символами
    def __str__(self):
        return self.title[:30]


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
        help_text='Комментарий к посту',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор поста',
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='Дата и время публикации комментария',
        auto_now_add=True
    )

    def __str__(self):
        return self.text[:15]
