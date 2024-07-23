from blazingapi.middleware import BaseMiddleware
from blazingapi.settings import settings


class XFrameOptionsMiddleware(BaseMiddleware):

    def execute_after(self, request, response):

        if response.headers.get('X-Frame-Options') is not None:
            return response

        response.headers['X-Frame-Options'] = getattr(settings, 'X_FRAME_OPTIONS', 'DENY').upper()

        return response


class CorsMiddleware(BaseMiddleware):

    def execute_after(self, request, response):

        origin = request.headers.get("Origin", "*")

        if "*" in settings.CORS_ALLOWED_ORIGINS or origin in settings.CORS_ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin if "*" not in settings.CORS_ALLOWED_ORIGINS else "*"
            response.headers['Access-Control-Allow-Methods'] = ",".join(settings.CORS_ALLOWED_METHODS)
            response.headers['Access-Control-Allow-Headers'] = ",".join(settings.CORS_ALLOWED_HEADERS)

        if request.method == "OPTIONS":
            response.status = 204
            response.body = ""

        return response
