import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings


class PasswordResetFlowTests(TestCase):
	@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
	def test_password_reset_end_to_end(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			email='reset-flow@example.com',
			password='InitialPass123!',
			first_name='Reset',
			last_name='Flow',
			user_type='1',
			gender='M',
			address='Test Address',
			profile_pic='',
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
