from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Allow username-based lookup as fallback where USERNAME_FIELD is not email.
            try:
                user = UserModel.objects.get(**{UserModel.USERNAME_FIELD: username})
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
