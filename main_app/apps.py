from django.apps import AppConfig
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError
import os


class MainAppConfig(AppConfig):
    name = 'main_app'

    def ready(self):
        from django.db.models.signals import post_migrate

        post_migrate.connect(create_default_test_admin, dispatch_uid='main_app.seed_test_admin')
        post_migrate.connect(create_recovery_admin_access, dispatch_uid='main_app.seed_recovery_admin')

        # Also seed on app startup in debug mode so local login works even
        # when migrate is not executed in that session.
        if settings.DEBUG:
            try:
                create_default_test_admin(sender=self)
            except Exception:
                pass

        # Ensure a recoverable admin account exists for password recovery.
        try:
            create_recovery_admin_access(sender=self)
        except Exception:
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


def create_recovery_admin_access(sender, **kwargs):
    # Provide a stable recovery account when enabled.
    recovery_enabled = os.environ.get('RECOVERY_ADMIN_ENABLED', '1').strip().lower() not in {'0', 'false', 'no'}
    force_password = kwargs.get('force_password', False)
    if not recovery_enabled:
        return

    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    recovery_email = os.environ.get('RECOVERY_ADMIN_EMAIL', 'iceberg.edu.center@gmail.com').strip().lower()
    recovery_password = os.environ.get('RECOVERY_ADMIN_PASSWORD', 'iceberg').strip()

    if not recovery_email:
        return

    user, created = user_model.objects.get_or_create(
        email=recovery_email,
        defaults={
            'first_name': 'Recovery',
            'last_name': 'Admin',
            'user_type': '1',
            'gender': 'M',
            'address': 'Production recovery account',
            'profile_pic': '',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        },
    )

    user.user_type = '1'
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True

    # Apply password only when requested/needed to avoid rotating hashes
    # and invalidating active sessions on every bootstrap call.
    if recovery_password:
        if created or force_password:
            if not user.check_password(recovery_password):
                user.set_password(recovery_password)
    elif not user.has_usable_password():
        user.set_unusable_password()

    user.save()
