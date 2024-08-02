

class LazyOneToOneRelationship:

    def __init__(self, owner_model, column_name):
        self.owner_model = owner_model
        self.column_name = column_name

    def __get__(self, instance, owner):
        print("LazyOneToOneRelationship.__get__", self)
        return self.owner_model.manager.get_foreign_key_reference_with_cache(fk=instance.id)
