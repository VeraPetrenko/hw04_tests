from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


CREATE_POST_URL = reverse('posts:post_create')
TEST_DATA = {
    'username': 'author',
    'test_group_title': 'Тестовая группа изначальная',
    'test_group_slug': 'test-slug',
    'test_group_description': 'Тестовое описание',
    'test_create_post_text': 'Тестовый пост при его создании',
    'test_edit_post_group_title': (
        'Тестовая группа для отредактированного поста'),
    'test_edit_post_group_slug': 'test-slug-edit',
    'test_edit_post_group_description': 'Тестовое описание новой группы',
    'test_edit_post_text': 'Тестовый текст поста при редактировании'
}


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_DATA['username'])
        cls.group = Group.objects.create(
            title=TEST_DATA['test_group_title'],
            slug=TEST_DATA['test_group_slug'],
            description=TEST_DATA['test_group_description'],
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': TEST_DATA['test_create_post_text'],
            'group': self.group.id,
        }
        self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        created_post = Post.objects.filter(
            text=TEST_DATA['test_create_post_text'],
            group=self.group.id
        ).first()
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group.id, form_data['group'])

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post_father = Post.objects.create(
            author=self.user,
            text=TEST_DATA['test_create_post_text'],
            group=self.group
        )
        POST_FATHER_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': post_father.id}
        )
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title=TEST_DATA['test_edit_post_group_title'],
            slug=TEST_DATA['test_edit_post_group_slug'],
            description=TEST_DATA['test_edit_post_group_description'],
        )
        form_data = {
            'text': TEST_DATA['test_edit_post_text'],
            'group': new_group.id,
        }
        response = self.authorized_client.post(
            POST_FATHER_EDIT_URL,
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.filter(id=post_father.id).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
