import importlib


class Settings:
    _instance = None

    def __new__(cls, settings_module='settings'):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_settings(settings_module)
        return cls._instance

    def _load_settings(self, settings_module):
        try:
            module = importlib.import_module(settings_module)
            for key in dir(module):
                if key.isupper():
                    value = getattr(module, key)
                    setattr(self, key, value)
        except ModuleNotFoundError as e:
            module = importlib.import_module('blazingapi.default_settings')
            for key in dir(module):
                if key.isupper():
                    value = getattr(module, key)
                    setattr(self, key, value)


settings = Settings()
