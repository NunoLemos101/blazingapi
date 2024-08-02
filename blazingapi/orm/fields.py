from enum import Enum

from blazingapi.orm.validators import EmailValidator, ChoiceValidator, MinValueValidator, MaxValueValidator, PositiveNumberValidator, NegativeNumberValidator, DateTimeValidator


class ForeignKeyAction(Enum):
    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


class Field:

    def __init__(self, field_type, default=None, nullable=True, unique=False, choices=None, validators=None):

        if nullable is False and default is None:
            raise ValueError("Non-nullable fields must have a default value")

        self.field_type = field_type
        self.default = default
        self.nullable = nullable
        self.unique = unique
        self.validators = [] if validators is None else validators
        if choices is not None:
            self.validators.append(ChoiceValidator(choices))

    def render_sql(self, name):
        null_constraint = "" if self.nullable else " NOT NULL"
        unique_constraint = " UNIQUE" if self.unique else ""

        # If default value is a function, let the application handle it
        if self.default is None or callable(self.default):
            default_constraint = ""
        elif isinstance(self.default, str):
            default_constraint = f' DEFAULT "{self.default}"'
        else:
            default_constraint = f' DEFAULT {self.default}'

        return f'"{name}" {self.field_type}{null_constraint}{unique_constraint}{default_constraint}'

    def validate(self, value):
        for validator in self.validators:
            validator(value)


class IntegerField(Field):
    """
    A field that stores integers.
    """

    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("INTEGER", default, nullable, unique, choices, validators)


class TextField(Field):
    """
    A field that stores text.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__('TEXT', default, nullable, unique, choices, validators)


class VarCharField(Field):
    """
    A field that stores variable-length strings.
    """
    def __init__(self, max_length, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(f'VARCHAR({max_length})', default, nullable, unique, choices, validators)
        self.max_length = max_length


class EmailField(Field):
    """
    A field that validates email addresses.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__('VARCHAR', default, nullable, unique, choices, validators)
        self.max_length = 256
        self.validators.append(EmailValidator())


class PrimaryKeyField(Field):
    """
    A field that is the primary key of the table.
    """
    def __init__(self):
        super().__init__("INTEGER PRIMARY KEY")


class ForeignKeyField(Field):
    """
    A field that references another model.
    """
    def __init__(self, reference_model, on_delete=ForeignKeyAction.CASCADE, on_update=ForeignKeyAction.CASCADE, related_name=None, default=None, nullable=True, validators=None):
        super().__init__(f'INTEGER', default=default, nullable=nullable, validators=validators)  # Assuming the reference is always an Integer ID for simplicity
        self.reference_model = reference_model
        self.on_delete = on_delete
        self.on_update = on_update
        self.related_name = related_name


    def render_foreign_key_sql(self, name):
        if self.reference_model is str:
            reference_table = self.reference_model
        else:
            reference_table = self.reference_model._table

        reference_field = 'id'
        return f'FOREIGN KEY("{name}") REFERENCES "{reference_table}" ("{reference_field}") ON DELETE {self.on_delete.value} ON UPDATE {self.on_update.value}'

    def __set_name__(self, owner, name):
        self.column_name = name

    def __get__(self, instance, owner):
        return self.reference_model.manager.get_foreign_key_reference_with_cache(fk=getattr(instance, f"_{self.column_name}_id"))


class OneToOneField(ForeignKeyField):
    """
    A field that references another model with a unique constraint.
    """
    def __init__(self, reference_model, on_delete=ForeignKeyAction.CASCADE, on_update=ForeignKeyAction.CASCADE, related_name=None, default=None, nullable=True, validators=None):
        super().__init__(f'INTEGER', default=default, nullable=nullable, validators=validators)
        self.reference_model = reference_model
        self.unique = True
        self.on_delete = on_delete
        self.on_update = on_update
        self.related_name = related_name

    def __get__(self, instance, owner):
        return self.reference_model.manager.get_foreign_key_reference_with_cache(fk=getattr(instance, f"_{self.column_name}_id"))


class PositiveIntegerField(Field):
    """
    A field that only accepts positive values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("INTEGER", default, nullable, unique, choices, validators)
        self.validators.append(PositiveNumberValidator())


class NegativeIntegerField(Field):
    """
    A field that only accepts negative values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("INTEGER", default, nullable, unique, choices, validators)
        self.validators.append(NegativeNumberValidator())


class NonPositiveIntegerField(Field):
    """
    A field that only accepts negative or zero values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("INTEGER", default, nullable, unique, choices, validators)
        self.validators.append(MaxValueValidator(0))


class NonNegativeIntegerField(Field):
    """
    A field that only accepts positive or zero values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("INTEGER", default, nullable, unique, choices, validators)
        self.validators.append(MinValueValidator(0))


class FloatField(Field):
    """
    A field that stores real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("REAL", default, nullable, unique, choices, validators)


class PositiveFloatField(Field):
    """
    A field that only accepts positive real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("REAL", default, nullable, unique, choices, validators)
        self.validators.append(PositiveNumberValidator())


class NegativeFloatField(Field):
    """
    A field that only accepts negative real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("REAL", default, nullable, unique, choices, validators)
        self.validators.append(NegativeNumberValidator())


class NonPositiveFloatField(Field):
    """
    A field that only accepts negative or zero real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("REAL", default, nullable, unique, choices, validators)
        self.validators.append(MaxValueValidator(0))


class NonNegativeFloatField(Field):
    """
    A field that only accepts positive or zero real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("REAL", default, nullable, unique, choices, validators)
        self.validators.append(MinValueValidator(0))


class DateTimeField(Field):
    """
    A field that stores date and time values.
    """

    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__("DATETIME", default, nullable, unique, choices, validators)
        self.validators.append(DateTimeValidator())
