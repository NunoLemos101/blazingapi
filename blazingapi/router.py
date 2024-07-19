import re

from framework.middleware import MiddlewareManager
from framework.request import Request


class Router:

    _middleware_manager = MiddlewareManager()

    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):

        request = Request.from_environ(environ)

        self.execute_all_middleware(request)

        response = self.handle_request(request)

        if response:

            self.execute_all_middleware_after(request, response)

            response_content = response.to_http_response()

            start_response(self.status_code_to_message(response.status), list(response.headers.items()))

            return [response_content['body'].encode()]

        else:
            # If no response was returned by the view function, return a 404 response
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'404 Not Found']

    def get(self, path: str):
        return self.add_route(path, "GET")

    def post(self, path: str):
        return self.add_route(path, "POST")

    def put(self, path: str):
        return self.add_route(path, "PUT")

    def delete(self, path: str):
        return self.add_route(path, "DELETE")

    def add_route(self, path: str, method: str):
        method = method.upper()
        path_regex = re.sub(r'{(\w+)}', r'(?P<\1>[^/]+)', path)

        if path_regex not in self.routes:
            self.routes[path_regex] = {}

        def decorator(handler):
            self.routes[path_regex][method] = handler
            return handler

        return decorator

    def resolve(self, path: str, method: str):
        method = method.upper()
        for path_regex, methods_dict in self.routes.items():
            match = re.match(f"^{path_regex}$", path)
            if match:
                handler = methods_dict.get(method)
                if handler:
                    return handler, match.groupdict()

        return None, {}

    def handle_request(self, request: Request):
        handler, path_params = self.resolve(request.path, request.method)
        if handler:
            return handler(request, **path_params)
        else:
            return None

    def add_middleware(self, middleware):
        self._middleware_manager.add_middleware(middleware)

    def execute_all_middleware(self, request):
        self._middleware_manager.execute_all(request)

    def execute_all_middleware_after(self, request, response):
        self._middleware_manager.execute_all_after(request, response)

    def status_code_to_message(self, status_code):
        status_messages = {
            200: "200 OK",
            201: "201 Created",
            202: "202 Accepted",
            204: "204 No Content",
            400: "400 Bad Request",
            401: "401 Unauthorized",
            403: "403 Forbidden",
            404: "404 Not Found",
            500: "500 Internal Server Error",
        }

        return status_messages.get(status_code, f"{status_code} Unknown Status Code")
