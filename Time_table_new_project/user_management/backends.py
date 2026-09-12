from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class EmailOrEmpIdBackend(ModelBackend):
    """Authenticate with username, email, OR employee ID -- whichever matches -- plus password."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        lookup = Q(username__iexact=username) | Q(email__iexact=username) | Q(emp_id__iexact=username)
        try:
            user = UserModel.objects.get(lookup)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(lookup).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
