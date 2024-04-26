from django.test import TestCase
from main_app.models import CustomUser
from main_app.EmailBackend import EmailBackend


class EmailBackendTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            user_type="1",
            gender="M",
        )

    def test_authenticate_with_valid_credentials(self):
        backend = EmailBackend()
        user = backend.authenticate(
            username="testuser@example.com", password="testpassword"
        )
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_email(self):
        backend = EmailBackend()
        user = backend.authenticate(
            username="invalidemail@example.com", password="testpassword"
        )
        self.assertIsNone(user)

    def test_authenticate_with_invalid_password(self):
        backend = EmailBackend()
        user = backend.authenticate(
            username="testuser@example.com", password="invalidpassword"
        )
        self.assertIsNone(user)

    def test_authenticate_with_missing_username(self):
        backend = EmailBackend()
        user = backend.authenticate(password="testpassword")
        self.assertIsNone(user)

    def test_authenticate_with_missing_password(self):
        backend = EmailBackend()
        user = backend.authenticate(username="testuser@example.com")
        self.assertIsNone(user)
