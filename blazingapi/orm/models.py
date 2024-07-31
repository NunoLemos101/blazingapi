import inspect

from blazingapi.orm.fields import Field, PrimaryKeyField, ForeignKeyField
from blazingapi.orm.manager import Manager
from blazingapi.orm.query import ConnectionPool


def accepts_kwargs(func):
    # Get the signature of the callable
    sig = inspect.signature(func)

    # Check if any parameter is of kind VAR_KEYWORD
    for param in sig.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        foreign_keys = {}

        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
            if isinstance(value, ForeignKeyField):
                foreign_keys[key] = value

        for base in bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)

        attrs['_fields'] = fields
        attrs['_foreign_keys'] = foreign_keys

        if '_table' not in attrs:
            attrs['_table'] = name.lower()

        new_class = super().__new__(cls, name, bases, attrs)
        new_class.manager = Manager(new_class)
        return new_class


class Model(metaclass=ModelMeta):
    """
    Base class for all models. Provides basic functionality
    for creating, updating, deleting and serializing models.
    """
    _fields = {}
    _foreign_keys = {}
    _table = None
    serializable_fields = '__all__'
    id = PrimaryKeyField()
    cache = {}

    def __init__(self, **kwargs):

        for field_name in kwargs:
            if field_name not in self._fields:
                raise AttributeError(f"Invalid field '{field_name}' for model '{self.__class__.__name__}'")

        for field_name in self._fields:
            value = kwargs.get(field_name)
            field = self._fields[field_name]
            if value is None and field.default is not None:
                if callable(field.default):
                    if accepts_kwargs(field.default):
                        value = field.default(**kwargs)
                    else:
                        value = field.default()
                else:
                    value = field.default

            if field_name in self._foreign_keys:
                if isinstance(value, Model):
                    setattr(self, field_name, value)
                else:
                    # This allows for lazy loading in the ForeignKeyField.__get__ method
                    setattr(self, f"_{field_name}_id", value)
            else:
                setattr(self, field_name, value)

    @classmethod
    def create_table(cls):
        connection = ConnectionPool.get_connection()
        fields = [field.render_sql(name) for name, field in cls._fields.items()]
        foreign_keys = [field.render_foreign_key_sql(name) for name, field in cls._fields.items() if isinstance(field, ForeignKeyField)]

        fields_str = ', '.join(fields)
        if foreign_keys:
            fields_str += ', ' + ', '.join(foreign_keys)

        sql_statement = f'CREATE TABLE IF NOT EXISTS {cls._table} ({fields_str})'

        connection.execute(sql_statement)
        print(sql_statement)

    def save(self):
        connection = ConnectionPool.get_connection()

        fields = []
        values = []

        for field_name in self._fields:
            value = getattr(self, field_name)

            field = self._fields[field_name]

            if value is None and field.default is not None:
                # The default values are all defined at __init__ method.
                # This condition is only met if the user explicitly sets some value to None
                # after the default value is generated at __init__.
                continue

            field.validate(value)

            fields.append(field_name)
            if isinstance(value, Model):
                if value.id is None:
                    value.save()
                values.append(getattr(value, "id"))
            else:
                values.append(value)

        field_str = ', '.join(fields)
        placeholder_str = ', '.join(['?'] * len(fields))
        print(f'INSERT INTO {self._table} ({field_str}) VALUES ({placeholder_str})', values)
        sql_statement = f'INSERT INTO {self._table} ({field_str}) VALUES ({placeholder_str})'
        cursor = connection.execute(sql_statement, values)

        self.id = cursor.lastrowid
        connection.commit()

    def update(self, **kwargs):

        fields = []

        # Validate fields
        for key in kwargs.keys():
            if key not in self._fields:
                raise AttributeError(f"Invalid field '{key}' for model '{self.__class__.__name__}'")

            self._fields[key].validate(kwargs[key])

            fields.append(f'{key}=?')

        connection = ConnectionPool.get_connection()
        sql_statement = f'UPDATE {self._table} SET {", ".join(fields)} WHERE id=?'
        values = list(kwargs.values()) + [self.id]

        connection.execute(sql_statement, values)

        connection.commit()

        # Update local attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def delete(self):
        connection = ConnectionPool.get_connection()
        connection.execute(f'DELETE FROM {self._table} WHERE id=?', [self.id])
        connection.commit()

    def serialize(self):

        result = {}

        serializable_fields = self._fields if self.serializable_fields == '__all__' else self.serializable_fields

        for field in serializable_fields:
            value = getattr(self, field)
            if isinstance(value, Model):
                result[field] = value.serialize()
            else:
                result[field] = value

        return result
