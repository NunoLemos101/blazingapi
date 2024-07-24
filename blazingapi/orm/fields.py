from enum import Enum


class ForeignKeyAction(Enum):
    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


class Field:

    def __init__(self, field_type, nullable=False, unique=False):
        self.field_type = field_type
        self.nullable = nullable
        self.unique = unique

    def render_sql(self, name):
        null_constraint = "" if self.nullable else " NOT NULL"
        unique_constraint = " UNIQUE" if self.unique else ""
        return f'"{name}" {self.field_type}{null_constraint}{unique_constraint}'


class IntegerField(Field):

    def __init__(self, nullable=False, unique=False):
        super().__init__("INTEGER", nullable, unique)


class TextField(Field):
    def __init__(self, nullable=False, unique=False):
        super().__init__('TEXT', nullable, unique)


class VarCharField(Field):
    def __init__(self, max_length, nullable=False, unique=False):
        super().__init__(f'VARCHAR({max_length})', nullable, unique)
        self.max_length = max_length


class PrimaryKeyField(Field):
    def __init__(self):
        super().__init__("INTEGER PRIMARY KEY")


class ForeignKeyField(Field):

    def __init__(self, reference_model, on_delete=ForeignKeyAction.CASCADE, on_update=ForeignKeyAction.CASCADE, nullable=False):
        super().__init__(f'INTEGER', nullable, False)  # Assuming the reference is always an Integer ID for simplicity
        self.reference_model = reference_model
        self.on_delete = on_delete
        self.on_update = on_update

    def render_sql(self, name):
        base_sql = super().render_sql(name)

        if self.reference_model is str:
            reference_table = self.reference_model
        else:
            reference_table = self.reference_model._table

        reference_field = 'id'  # Assuming the reference field is always 'id'
        fk_constraint = f', FOREIGN KEY("{name}") REFERENCES "{reference_table}" ("{reference_field}") ON DELETE {self.on_delete.value} ON UPDATE {self.on_update.value}'
        return base_sql + fk_constraint
