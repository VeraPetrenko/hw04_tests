from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User
from users.forms import CreationForm


SIGNUP_URL = reverse('users:signup')
TEST_DATA = {
    'username': 'TestUserName',
    'first_name': 'Test_first_name',
    'last_name': 'Test_last_name',
    'email': 'TestEmail@yandex.ru',
    'password': 'Test_Password1',
}


class UserTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()
        cls.guest_client = Client()

    def test_create_user_from_signup_page(self):
        """При заполнении формы signup создается новый пользователь"""
        users_start_count = User.objects.count()
        form_data = {
            'first_name': TEST_DATA['first_name'],
            'last_name': TEST_DATA['last_name'],
            'username': TEST_DATA['username'],
            'email': TEST_DATA['email'],
            'password1': TEST_DATA['password'],
            'password2': TEST_DATA['password']
        }
        response = self.guest_client.post(SIGNUP_URL, form_data)
        users_end_count = User.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(users_end_count, users_start_count + 1)
