import importlib
import inspect

from gunicorn.app.base import BaseApplication

from framework.app import app
from framework.orm.models import Model
from framework.settings import settings


class StandaloneApplication(BaseApplication):
    def __init__(self, application, options=None):
        self.options = options or {}
        self.application = application
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application



def import_view_modules():
    for module_name in settings.VIEW_FILES:
        importlib.import_module(module_name)


def create_all_tables():
    for module_name in settings.MODEL_FILES:
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Model) and obj is not Model:
                obj.create_table()


def add_middlewares():
    for middleware_path in settings.MIDDLEWARE_CLASSES:
        module_path, class_name = middleware_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        middleware_class = getattr(module, class_name)

        app.add_middleware(middleware_class())


def run(port: int = 8000):

    import_view_modules()
    create_all_tables()
    add_middlewares()

    options = {
        'bind': '%s:%s' % ('0.0.0.0', port),
        'workers': 4,
    }
    StandaloneApplication(app, options).run()
