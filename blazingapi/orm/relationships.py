

class LazyOneToOneRelationship:

    def __init__(self, owner_model, id, column_name):
        self.owner_model = owner_model
        self.id = id
        self.column_name = column_name

    def __get__(self, instance, owner):
        print("LazyOneToOneRelationship.__get__", instance, owner)
        return self.owner_model.manager.get_foreign_key_reference_with_cache(fk=self.id)
