from blazingapi.auth.models import AnonymousUser
from blazingapi.auth.exceptions import AuthenticationFailedException


class IsAuthenticated:

    def __call__(self, request):
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            raise AuthenticationFailedException()
