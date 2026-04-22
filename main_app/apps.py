from django.apps import AppConfig
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError
import os


class MainAppConfig(AppConfig):
    name = 'main_app'

    def ready(self):
        from django.db.models.signals import post_migrate

        post_migrate.connect(create_default_test_admin, dispatch_uid='main_app.seed_test_admin')

        # Also seed on app startup in debug mode so local login works even
        # when migrate is not executed in that session.
        if settings.DEBUG:
            try:
                create_default_test_admin(sender=self)
            except (OperationalError, ProgrammingError):
                # Database tables may not exist yet during early startup.
                pass


def create_default_test_admin(sender, **kwargs):
    # Create a predictable admin account only for local debug/testing use.
    if not settings.DEBUG:
        return

    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    email = os.environ.get('TEST_ADMIN_EMAIL', 'admin@test.com')
    password = os.environ.get('TEST_ADMIN_PASSWORD', 'admin123')

    user, created = user_model.objects.get_or_create(
        email=email,
        defaults={
            'first_name': 'Test',
            'last_name': 'Admin',
            'user_type': '1',
            'gender': 'M',
            'address': 'Test Admin Account',
            'profile_pic': '',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        },
    )

    # Keep local debug login deterministic even if the record already exists.
    user.first_name = user.first_name or 'Test'
    user.last_name = user.last_name or 'Admin'
    user.user_type = '1'
    user.gender = user.gender or 'M'
    user.address = user.address or 'Test Admin Account'
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
