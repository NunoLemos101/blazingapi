from enum import Enum

from blazingapi.orm.validators import EmailValidator, ChoiceValidator, MinValueValidator, MaxValueValidator, PositiveNumberValidator, NegativeNumberValidator, DateTimeValidator


class ForeignKeyAction(Enum):
    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


class Field:

    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        if nullable is False and default is None:
            raise ValueError("Non-nullable fields must have a default value")

        self.default = default
        self.nullable = nullable
        self.unique = unique
        self.validators = [] if validators is None else validators
        if choices is not None:
            self.validators.append(ChoiceValidator(choices))

    def validate(self, value):
        for validator in self.validators:
            validator(value)


class IntegerField(Field):
    """
    A field that stores integers.
    """

    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)


class TextField(Field):
    """
    A field that stores text.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)


class VarCharField(Field):
    """
    A field that stores variable-length strings.
    """
    def __init__(self, max_length, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.max_length = max_length
        self.field_type = self.field_type % {'max_length': max_length}


class EmailField(Field):
    """
    A field that validates email addresses.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.max_length = 256
        self.validators.append(EmailValidator())


class PrimaryKeyField(Field):
    """
    A field that is the primary key of the table.
    """
    def __init__(self):
        super().__init__()


class ForeignKeyField(Field):
    """
    A field that references another model.
    """
    def __init__(self, reference_model, on_delete=ForeignKeyAction.CASCADE, on_update=ForeignKeyAction.CASCADE, related_name=None, default=None, nullable=True, validators=None):
        super().__init__(default=default, nullable=nullable, validators=validators)  # Assuming the reference is always an Integer ID for simplicity
        self.reference_model = reference_model
        self.on_delete = on_delete
        self.on_update = on_update
        self.related_name = related_name

    def __set_name__(self, owner, name):
        self.column_name = name

    def __get__(self, instance, owner):
        return self.reference_model.manager.get_foreign_key_reference_with_cache(fk=getattr(instance, f"_{self.column_name}_id"))


class OneToOneField(ForeignKeyField):
    """
    A field that references another model with a unique constraint.
    """
    def __init__(self, reference_model, on_delete=ForeignKeyAction.CASCADE, on_update=ForeignKeyAction.CASCADE, related_name=None, default=None, nullable=True, validators=None):
        super().__init__(reference_model, default=default, nullable=nullable, validators=validators)
        self.reference_model = reference_model
        self.unique = True
        self.on_delete = on_delete
        self.on_update = on_update
        self.related_name = related_name

    def __get__(self, instance, owner):
        """
        This method is triggered when the field is accessed directly.
        """
        return self.reference_model.manager.get_foreign_key_reference_with_cache(fk=getattr(instance, f"_{self.column_name}_id"))


class PositiveIntegerField(Field):
    """
    A field that only accepts positive values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(PositiveNumberValidator())


class NegativeIntegerField(Field):
    """
    A field that only accepts negative values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(NegativeNumberValidator())


class NonPositiveIntegerField(Field):
    """
    A field that only accepts negative or zero values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(MaxValueValidator(0))


class NonNegativeIntegerField(Field):
    """
    A field that only accepts positive or zero values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(MinValueValidator(0))


class FloatField(Field):
    """
    A field that stores real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)


class PositiveFloatField(Field):
    """
    A field that only accepts positive real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(PositiveNumberValidator())


class NegativeFloatField(Field):
    """
    A field that only accepts negative real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(NegativeNumberValidator())


class NonPositiveFloatField(Field):
    """
    A field that only accepts negative or zero real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(MaxValueValidator(0))


class NonNegativeFloatField(Field):
    """
    A field that only accepts positive or zero real values.
    """
    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(MinValueValidator(0))


class DateTimeField(Field):
    """
    A field that stores date and time values.
    """

    def __init__(self, default=None, nullable=True, unique=False, choices=None, validators=None):
        super().__init__(default, nullable, unique, choices, validators)
        self.validators.append(DateTimeValidator())
