

class LazyOneToOneReverseRelationship:

    def __init__(self, owner_model, column_name):
        self.owner_model = owner_model
        self.column_name = column_name

    def __get__(self, instance, owner):
        return self.owner_model.manager.filter(**{f"{self.column_name}": instance.id}).get()