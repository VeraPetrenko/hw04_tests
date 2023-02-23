from django.test import TestCase

from posts.models import Group, Post, User


TEST_DATA = {
    'username': 'author',
    'test_group_title': 'Тестовая группа',
    'test_group_slug': 'test-slug',
    'test_group_description': 'Тестовое описание',
    'test_post_text': 'Тестовый пост',
}
POST_FIELDS_VERBOSES = {
    'text': 'Текст поста',
    'pub_date': 'Дата публикации',
    'author': 'Автор поста',
    'group': 'Группа',
}
POSTS_FIELDS_HELP_TEXT = {
    'text': 'Введите текст поста',
    'group': 'Группа, к которой будет относиться пост',
    'image': 'Загрузите картинку',
}


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_DATA['username'])
        cls.group = Group.objects.create(
            title=TEST_DATA['test_group_title'],
            slug=TEST_DATA['test_group_slug'],
            description=TEST_DATA['test_group_description'],
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_DATA['test_post_text'],
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_object_names = {
            str(self.post): TEST_DATA['test_post_text'],
            str(self.group): TEST_DATA['test_group_title'],
        }
        for object_name, expected_value in models_object_names.items():
            with self.subTest(object_name=object_name):
                self.assertEqual(
                    object_name,
                    expected_value,
                    '__str__ работает неправильно')

    def test_post_model_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post

        for field, expected_value in POST_FIELDS_VERBOSES.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value,
                    'verbose_name работает неправильно')

    def test_post_model_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        for field, expected_value in POSTS_FIELDS_HELP_TEXT.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                    'help_text работает неправильно')
