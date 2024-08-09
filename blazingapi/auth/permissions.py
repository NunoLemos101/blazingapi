from blazingapi.auth.models import AnonymousUser
from blazingapi.auth.exceptions import AuthenticationFailedException
from blazingapi.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def __call__(self, request):
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            raise AuthenticationFailedException()
