from blazingapi.orm.query import QuerySet


class Manager:

    def __init__(self, model):
        self.model = model

    def all(self):
        return QuerySet(self.model).all()

    def filter(self, *args, **kwargs):
        return QuerySet(self.model).filter(*args, **kwargs)

    def get(self, *args, **kwargs):
        return QuerySet(self.model).filter(*args, **kwargs).get()
