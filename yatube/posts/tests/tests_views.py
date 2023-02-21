from django import forms
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
    'test_new_group_title': 'Новая тестовая группа',
    'test_new_group_slug': 'test-slug-new',
    'test_new_group_description': 'Тестовое описание новой группы',
}


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title=TEST_DATA['test_group_title'],
            slug=TEST_DATA['test_group_slug'],
            description=TEST_DATA['test_group_description'],
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_DATA['test_post_text'],
            group=cls.group,
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            CREATE_POST_URL: 'posts/post_create.html',
            self.POST_EDIT_URL: 'posts/post_create.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        first_object = response.context['page_obj'][0]
        first_post_author = first_object.author
        first_post_text = first_object.text
        self.assertEqual(first_post_author, self.post.author)
        self.assertEqual(first_post_text, self.post.text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.GROUP_LIST_URL
        )
        self.assertEqual(
            response.context['group'].title,
            self.group.title
        )
        self.assertEqual(
            response.context['group'].description,
            self.group.description
        )
        if response.context['page_obj'][0]:
            first_object = response.context['page_obj'][0]
            first_post_group = first_object.group
            self.assertEqual(first_post_group, self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.PROFILE_URL
        )
        user_from_context = response.context['author']
        self.assertEqual(self.user, user_from_context)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.POST_DETAIL_URL
        )
        post_context = response.context['post'].id
        self.assertEqual(post_context, self.post.id)

    def test_areate_and_edit_post_page_show_correct_context(self):
        """Шаблон create_post в части создания и редактирования
        поста сформирован с правильным контекстом."""
        urls = [
            CREATE_POST_URL,
            self.POST_EDIT_URL
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for url in urls:
            response = self.authorized_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_show_post_after_creating(self):
        """При создании поста с группой он появляется на страницах"""
        reverse_pages = [
            INDEX_URL,
            self.GROUP_LIST_URL,
            self.PROFILE_URL
        ]
        for reverse_page in reverse_pages:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                first_post = response.context['page_obj'][0]
                self.assertEqual(first_post, self.post)

    def test_post_does_not_shows_on_incorrect_group_page(self):
        """Пост не отображается на странице группы,
        которой этот пост не принадлежит"""
        new_group = Group.objects.create(
            title=TEST_DATA['test_new_group_title'],
            slug=TEST_DATA['test_new_group_slug'],
            description=TEST_DATA['test_new_group_description'],
        )
        GROUP_LIST_URL = reverse(
            'posts:group_list',
            kwargs={'slug': new_group.slug}
        )
        response = self.authorized_client.get(
            GROUP_LIST_URL
        )
        page_objes = response.context['page_obj']
        for post in page_objes:
            self.assertEqual(post.group, new_group)


class PaginatorViewsTest(TestCase):
    POST_ON_PAGE = 10

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_DATA['username'])
        cls.group = Group.objects.create(
            title=TEST_DATA['test_new_group_title'],
            slug=TEST_DATA['test_new_group_slug'],
            description=TEST_DATA['test_new_group_description']
        )
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.PROFILE_URL = reverse(
            'posts:profile',
            kwargs={'username': cls.user.username}
        )

        cls.post_list = []
        # Для теста создается 13 постов
        for post in range(13):
            cls.post_list.append(
                Post.objects.create(
                    author=cls.user,
                    text=f'Тестовый пост {post}',
                    group=cls.group,
                )
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """На первой странице шаблона отображается десять постов."""
        reverses_for_paging = [
            INDEX_URL,
            self.GROUP_LIST_URL,
            self.PROFILE_URL
        ]
        for reverse_page in reverses_for_paging:
            with self.subTest(reverse_page=reverse_page):
                response = self.guest_client.get(reverse_page)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.POST_ON_PAGE
                )

    def test_second_page_contains_three_records(self):
        """На второй странице шаблона отображается три поста"""
        reverses_for_paging = [
            INDEX_URL,
            self.GROUP_LIST_URL,
            self.PROFILE_URL
        ]
        for reverse_page in reverses_for_paging:
            with self.subTest(reverse_page=reverse_page):
                response = self.guest_client.get(
                    reverse_page + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 3)
