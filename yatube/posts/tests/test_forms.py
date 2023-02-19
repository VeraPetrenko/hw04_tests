from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


from posts.forms import PostForm
from posts.models import Post, Group


User = get_user_model()


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа изначальная',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста при его создании',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст поста при его создании',
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post_father = Post.objects.create(
            author=self.user,
            text='Тестовый пост изначальный',
            group=self.group
        )
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title='Тестовая группа для отредактированного поста',
            slug='test-slug-edit',
            description='Тестовое описание новой группы',
        )
        form_data = {
            'text': 'Тестовый текст поста при редактировании',
            'group': new_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_father.id}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.filter(id=post_father.id).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
