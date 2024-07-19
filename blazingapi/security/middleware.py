from framework.middleware import BaseMiddleware
from framework.settings import settings


class XFrameOptionsMiddleware(BaseMiddleware):

    def execute_after(self, request, response):

        if response.headers.get('X-Frame-Options') is not None:
            return response

        response.headers['X-Frame-Options'] = getattr(settings, 'X_FRAME_OPTIONS', 'DENY').upper()

        return response
