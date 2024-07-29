

class MiddlewareManager:

    middleware_instances = []

    def add_middleware(self, middleware):
        self.middleware_instances.append(middleware)

    def execute_all(self, request):

        for middleware in self.middleware_instances:
            middleware.execute_before(request)

    def execute_all_after(self, request, response):
        for middleware in reversed(self.middleware_instances):
            middleware.execute_after(request, response)


class BaseMiddleware:

    def execute_before(self, request):
        """
        Code to be executed before the view or next middleware is called.
        """

    def execute_after(self, request, response):
        """
        Code to be executed after the view or next middleware is called on the way out.

        This function is called in reverse order of the middleware stack and can be used
        to modify the response before being returned to the user.
        """

