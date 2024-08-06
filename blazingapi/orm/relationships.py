

class LazyOneToOneReverseRelationship:

    def __init__(self, owner_model, id, column_name):
        self.owner_model = owner_model
        self.id = id
        self.column_name = column_name
        self.cache = {}

    def lazy_load(self):
        """
        This method is called when the reverse relationship in a ForeignKeyField is accessed.
        """
        if self.id in self.cache:
            return self.cache[self.id]

        result = self.owner_model.manager.filter(**{self.column_name: self.id}).get()
        self.cache[self.id] = result
        return result
