from blazingapi.orm.query import QuerySet


class Manager:

    cache = {}

    def __init__(self, model):
        self.model = model

    def all(self):
        return QuerySet(self.model).all()

    def filter(self, *args, **kwargs):
        return QuerySet(self.model).filter(*args, **kwargs)

    def get(self, *args, **kwargs):
        return QuerySet(self.model).filter(*args, **kwargs).get()

    def get_foreign_key_reference_with_cache(self, fk):
        """
        Should be used only internally to retrieve a model instance from a foreign key reference.

        This prevents multiple queries for the same foreign key reference.
        """
        if fk in self.cache:
            return self.cache[fk]

        obj = QuerySet(self.model).filter(id=fk).get()
        self.cache[fk] = obj
        return obj
