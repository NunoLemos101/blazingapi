from framework.auth.models import User, AnonymousUser
from framework.middleware import BaseMiddleware


class BearerAuthenticationMiddleware(BaseMiddleware):

    def execute_before(self, request) -> None:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            request.user = AnonymousUser()
            return

        token = auth_header.split(' ')[1]
        user = User.manager.get(token=token)

        if user is None:
            request.user = AnonymousUser()
            return

        request.user = user
