import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


_BASE_OVERRIDES = dict(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    SECURE_SSL_REDIRECT=False,
)


class LoginPageTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.admin = UserModel.objects.create_user(
            email='admin@example.com', password='AdminPass123!',
            first_name='Test', last_name='Admin', user_type='1',
            gender='M', address='Test', profile_pic='',
        )
        self.staff = UserModel.objects.create_user(
            email='staff@example.com', password='StaffPass123!',
            first_name='Test', last_name='Staff', user_type='2',
            gender='M', address='Test', profile_pic='',
        )
        self.student = UserModel.objects.create_user(
            email='student@example.com', password='StudentPass123!',
            first_name='Test', last_name='Student', user_type='3',
            gender='M', address='Test', profile_pic='',
        )

    @override_settings(**_BASE_OVERRIDES)
    def test_login_page_get_returns_200(self):
        response = self.client.get(reverse('login_page'))
        self.assertEqual(response.status_code, 200)

    @override_settings(**_BASE_OVERRIDES)
    def test_login_invalid_credentials_shows_error(self):
        response = self.client.post(reverse('user_login'), {
            'email': 'nobody@example.com', 'password': 'wrongpassword',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.content)

    @override_settings(**_BASE_OVERRIDES)
    def test_admin_login_redirects_to_admin_home(self):
        response = self.client.post(reverse('user_login'), {
            'email': 'admin@example.com', 'password': 'AdminPass123!',
        })
        self.assertRedirects(response, reverse('admin_home'), fetch_redirect_response=False)

    @override_settings(**_BASE_OVERRIDES)
    def test_staff_login_redirects_to_staff_home(self):
        response = self.client.post(reverse('user_login'), {
            'email': 'staff@example.com', 'password': 'StaffPass123!',
        })
        self.assertRedirects(response, reverse('staff_home'), fetch_redirect_response=False)

    @override_settings(**_BASE_OVERRIDES)
    def test_student_login_redirects_to_student_home(self):
        response = self.client.post(reverse('user_login'), {
            'email': 'student@example.com', 'password': 'StudentPass123!',
        })
        self.assertRedirects(response, reverse('student_home'), fetch_redirect_response=False)

    @override_settings(**_BASE_OVERRIDES)
    def test_no_role_confusion_admin_cannot_reach_student_home(self):
        self.client.login(username='admin@example.com', password='AdminPass123!')
        response = self.client.get(reverse('student_home'))
        self.assertNotEqual(response.status_code, 200)

    @override_settings(**_BASE_OVERRIDES)
    def test_unauthenticated_blocked_from_admin_home(self):
        response = self.client.get(reverse('admin_home'))
        self.assertNotEqual(response.status_code, 200)


class PasswordResetFlowTests(TestCase):
    @override_settings(**_BASE_OVERRIDES)
    def test_password_reset_end_to_end(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            email='reset-flow@example.com', password='InitialPass123!',
            first_name='Reset', last_name='Flow', user_type='1',
            gender='M', address='Test Address', profile_pic='',
        )

        response = self.client.post('/accounts/password_reset/', {'email': user.email}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        body = mail.outbox[0].body
        match = re.search(r'https?://[^\s]+/accounts/reset/[^\s]+', body)
        self.assertIsNotNone(match)

        token_path = '/' + match.group(0).split('/', 3)[3]
        confirm_get_response = self.client.get(token_path, follow=True)
        final_path = confirm_get_response.wsgi_request.path

        new_password = 'ChangedPass123!'
        confirm_post_response = self.client.post(
            final_path,
            {'new_password1': new_password, 'new_password2': new_password},
            follow=True,
        )

        self.assertEqual(confirm_post_response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))


class LoginFlowResilienceTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            email='admin-login@example.com', password='AdminPass123!',
            first_name='Admin', last_name='User', user_type='1',
            gender='M', address='Admin Address', profile_pic='',
        )

    @override_settings(SECURE_SSL_REDIRECT=False)
    @patch('main_app.views.login', side_effect=Exception('session backend unavailable'))
    def test_login_failure_is_handled_without_500(self, _mock_login):
        response = self.client.post(
            '/doLogin/',
            {'email': self.user.email, 'password': 'AdminPass123!'},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
