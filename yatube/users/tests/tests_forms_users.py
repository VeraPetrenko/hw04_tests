from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..forms import CreationForm


User = get_user_model()


class UserTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()
        cls.guest_client = Client()
        cls.username = 'TestUserName'
        cls.first_name = 'Test_first_name'
        cls.last_name = 'Test_last_name'
        cls.email = 'TestEmail@yandex.ru'
        cls.password = 'Test_Password1'

    def test_create_user_from_signup_page(self):
        """При заполнении формы signup создается новый пользователь"""
        users_start_count = User.objects.count()
        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password
        }
        response = self.guest_client.post(reverse('users:signup'), form_data)
        users_end_count = User.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(users_end_count, users_start_count + 1)
