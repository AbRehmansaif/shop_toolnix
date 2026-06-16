from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # We allow 'username' here because Django's default forms pass the email field as 'username'
        try:
            # We strictly check for email match here.
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            # Run password hasher once to prevent timing attacks
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            # If multiple users have the same email, get the first one (edge case)
            user = UserModel.objects.filter(email__iexact=username).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
