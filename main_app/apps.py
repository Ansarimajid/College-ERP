from django.apps import AppConfig
from django.conf import settings
import os


class MainAppConfig(AppConfig):
    name = 'main_app'

    def ready(self):
        from django.db.models.signals import post_migrate

        post_migrate.connect(create_default_test_admin, sender=self)


def create_default_test_admin(sender, **kwargs):
    # Create a predictable admin account only for local debug/testing use.
    if not settings.DEBUG:
        return

    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    email = os.environ.get('TEST_ADMIN_EMAIL', 'admin@test.com')
    password = os.environ.get('TEST_ADMIN_PASSWORD', 'admin123')

    if user_model.objects.filter(email=email).exists():
        return

    user_model.objects.create_superuser(
        email=email,
        password=password,
        first_name='Test',
        last_name='Admin',
        user_type='1',
        gender='M',
        address='Test Admin Account',
        profile_pic='',
    )
