from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


INDEX_URL = reverse('posts:index')
CREATE_POST_URL = reverse('posts:post_create')
UNEXISTING_PAGE_URL = '/unexisting_page/'
REDIRECT_CREATE_POST_URL = '/auth/login/?next=/create/'
TEST_DATA = {
    'username': 'author',
    'test_group_title': 'Тестовая группа',
    'test_group_slug': 'test-slug',
    'test_group_description': 'Тестовое описание',
    'test_post_text': 'Тестовый пост',
}


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=TEST_DATA['username']
        )
        cls.group = Group.objects.create(
            title=TEST_DATA['test_group_title'],
            slug=TEST_DATA['test_group_slug'],
            description=TEST_DATA['test_group_description'],
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_DATA['test_post_text']
        )
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.PROFILE_URL = reverse(
            'posts:profile',
            kwargs={'username': cls.user.username}
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_unexisting_page_returns_404_error(self):
        """Несуществующая страница возвращает ошибку 404"""
        response = self.guest_client.get(UNEXISTING_PAGE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_about_urls_exist_at_desired_location_for_guest(self):
        """Проверка доступности адресов для любого пользователя"""
        responses_urls = [
            INDEX_URL,
            self.GROUP_LIST_URL,
            self.PROFILE_URL,
            self.POST_DETAIL_URL,
        ]
        for url in responses_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Не доступен адрес {url}'
                )

    def test_about_create_post_url_exists_for_authorized(self):
        """Страница создания поста доступна для авторизованного пользователя"""
        response = self.authorized_client.get(
            CREATE_POST_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_edit_post_url_exists_for_authorized(self):
        """Страница редактирования поста доступна для автора поста"""
        response = self.authorized_client.get(
            self.POST_EDIT_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_create_post_url_exists_for_authorized(self):
        """Страница редактирования поста недоступна для любого пользователя"""
        response = self.guest_client.get(
            self.POST_EDIT_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_about_create_post_url_redirect_guest_on_login(self):
        """Страница создания поста перенаправит неавторизованного
        пользователя на страницу логина
        """
        response = self.guest_client.get(
            CREATE_POST_URL,
            follow=True
        )
        self.assertRedirects(
            response,
            (REDIRECT_CREATE_POST_URL)
        )
