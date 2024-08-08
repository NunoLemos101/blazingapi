from functools import wraps

from blazingapi.auth.models import AnonymousUser
from blazingapi.response import Response


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            return Response(body={"error": "Authentication required"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
