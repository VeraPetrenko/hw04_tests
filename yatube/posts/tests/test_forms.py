from http import HTTPStatus
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, override_settings, TestCase
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
    'test_edit_post_text': 'Тестовый текст поста при редактировании',
    'test_image': (
        (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
    ),
    'test_image_directory': 'posts/test_image.gif'
}
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.uploaded = SimpleUploadedFile(
            name='test_image.gif',
            content=TEST_DATA['test_image'],
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

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': TEST_DATA['test_create_post_text'],
            'group': self.group.id,
            'image': self.uploaded,
        }
        self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text=TEST_DATA['test_create_post_text'],
            group=self.group.id,
            image=TEST_DATA['test_image_directory']
        ).exists()
        )
        created_post = Post.objects.filter(
            text=TEST_DATA['test_create_post_text'],
            group=self.group.id,
            image=str(TEST_DATA['test_image_directory'])
        ).first()
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group.id, form_data['group'])
        self.assertEqual(str(created_post.image), 'posts/' + str(form_data['image']))

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post_father = Post.objects.create(
            author=self.user,
            text=TEST_DATA['test_create_post_text'],
            group=self.group,
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
            # 'image': self.uploaded,
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
        # self.assertEqual(str(edited_post.image), str(form_data['image']))
