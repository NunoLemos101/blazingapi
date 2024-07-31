from enum import Enum


class ForeignKeyAction(Enum):
    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


class Field:

    def __init__(self, field_type, nullable=False, unique=False, validators=None):
        self.field_type = field_type
        self.nullable = nullable
        self.unique = unique
        self.validators = [] if validators is None else validators

    def render_sql(self, name):
        null_constraint = "" if self.nullable else " NOT NULL"
        unique_constraint = " UNIQUE" if self.unique else ""
        return f'"{name}" {self.field_type}{null_constraint}{unique_constraint}'

    def validate(self, value):
        for validator in self.validators:
            validator(value)


class IntegerField(Field):

    def __init__(self, nullable=False, unique=False, validators=None):
        super().__init__("INTEGER", nullable, unique, validators)


class TextField(Field):
    def __init__(self, nullable=False, unique=False, validators=None):
        super().__init__('TEXT', nullable, unique, validators)


class VarCharField(Field):
    def __init__(self, max_length, nullable=False, unique=False, validators=None):
        super().__init__(f'VARCHAR({max_length})', nullable, unique, validators)
        self.max_length = max_length


class PrimaryKeyField(Field):
    def __init__(self):
        super().__init__("INTEGER PRIMARY KEY")


class ForeignKeyField(Field):

    def __init__(self, reference_model, on_delete=ForeignKeyAction.CASCADE, on_update=ForeignKeyAction.CASCADE, nullable=False, validators=None):
        super().__init__(f'INTEGER', nullable, False, validators)  # Assuming the reference is always an Integer ID for simplicity
        self.reference_model = reference_model
        self.on_delete = on_delete
        self.on_update = on_update

    def render_sql(self, name):
        return super().render_sql(name)

    def render_foreign_key_sql(self, name):
        if self.reference_model is str:
            reference_table = self.reference_model
        else:
            reference_table = self.reference_model._table

        reference_field = 'id'
        return f'FOREIGN KEY("{name}") REFERENCES "{reference_table}" ("{reference_field}") ON DELETE {self.on_delete.value} ON UPDATE {self.on_update.value}'

    def __get__(self, instance, owner):
        return self.reference_model.manager.get_foreign_key_reference_with_cache(fk=getattr(instance, f"_{self.reference_model._table}_id"))
