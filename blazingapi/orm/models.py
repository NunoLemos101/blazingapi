import copy
import inspect

from blazingapi.orm.engines import SQLiteEngine, PostgresSQLEngine, ConnectionPool
from blazingapi.orm.fields import Field, PrimaryKeyField, ForeignKeyField, OneToOneField
from blazingapi.orm.managers import Manager, RelatedModelManager
from blazingapi.orm.relationships import LazyOneToOneReverseRelationship
from blazingapi.settings import settings


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

        if name == "Model":
            if settings.DB_CONNECTION["driver"] == "sqlite":
                attrs['engine'] = SQLiteEngine()
            elif settings.DB_CONNECTION["driver"] == "postgres":
                attrs['engine'] = PostgresSQLEngine()

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
        for key, value in foreign_keys.items():
            related_fields = copy.deepcopy(getattr(value.reference_model, '_related_fields'))
            related_name = value.related_name if value.related_name is not None else f'{new_class._table}_set'
            related_fields[related_name] = {'model': new_class, 'column_name': key, "field": value, "is_one_to_one_relationship": isinstance(value, OneToOneField)}
            setattr(value.reference_model, '_related_fields', related_fields)
        return new_class


class Model(metaclass=ModelMeta):
    """
    Base class for all models. Provides basic functionality
    for creating, updating, deleting and serializing models.
    """
    _fields = {}
    _foreign_keys = {}
    _related_fields = {}
    _table = None
    serializable_fields = '__all__'
    depth_serialization_fields = []
    id = PrimaryKeyField()
    cache = {}
    engine: SQLiteEngine | PostgresSQLEngine = None

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
                if isinstance(value, Model) and type(field) == ForeignKeyField:
                    setattr(self, field_name, value)
                    foreign_key = self._foreign_keys[field_name]
                    related_name = foreign_key.related_name
                    if foreign_key.related_name is None:
                        related_name = f'{self._table}_set'
                    setattr(value, related_name, RelatedModelManager(self.__class__, value, field.column_name))
                else:
                    setattr(self, f"_{field_name}_id", value)
            else:
                setattr(self, field_name, value)

        for related_field in self._related_fields:
            context = self._related_fields[related_field]
            if context["is_one_to_one_relationship"]:
                one_to_one_relationship = LazyOneToOneReverseRelationship(context["model"], self.id, context["column_name"])
                setattr(self, f"one_to_one_{related_field}", one_to_one_relationship)
            else:
                manager = RelatedModelManager(context["model"], self, context["column_name"])
                setattr(self, related_field, manager)

    @classmethod
    def create_table(cls):
        connection = ConnectionPool.get_connection(cls.engine)
        cursor = connection.cursor()
        fields = [field.render_sql(name) for name, field in cls._fields.items()]
        foreign_keys = [field.render_foreign_key_sql(name) for name, field in cls._fields.items() if
                        isinstance(field, ForeignKeyField)]

        fields_str = ', '.join(fields)
        if foreign_keys:
            fields_str += ', ' + ', '.join(foreign_keys)

        sql_statement = f'CREATE TABLE IF NOT EXISTS {cls._table} ({fields_str})'
        cursor.execute(sql_statement)

        connection.commit()

    def save(self):
        connection = ConnectionPool.get_connection(self.engine)
        cursor = connection.cursor()
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

        sql_statement, values = self.engine.generate_insert_statement(self._table, fields, values)
        print(sql_statement)
        cursor.execute(sql_statement, values)

        self.id = cursor.lastrowid
        connection.commit()

    def update(self, **kwargs):

        fields = []

        # Validate fields
        for key in kwargs.keys():
            if key not in self._fields:
                raise AttributeError(f"Invalid field '{key}' for model '{self.__class__.__name__}'")

            self._fields[key].validate(kwargs[key])

            fields.append(f'{key}={self.engine.placeholder}')

        connection = ConnectionPool.get_connection(self.engine)
        cursor = connection.cursor()
        sql_statement = f'UPDATE {self._table} SET {", ".join(fields)} WHERE id={self.engine.placeholder}'
        values = list(kwargs.values()) + [self.id]

        cursor.execute(sql_statement, values)

        connection.commit()

        # Update local attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def delete(self):
        connection = ConnectionPool.get_connection(self.engine)
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {self._table} WHERE id={self.engine.placeholder}', [self.id])
        connection.commit()

    def serialize(self):
        result = {}

        serializable_fields = self._fields if self.serializable_fields == '__all__' else self.serializable_fields

        for field in serializable_fields:
            value = getattr(self, field)
            if isinstance(value, Model):
                if field in self.depth_serialization_fields:
                    result[field] = value.serialize()
                else:
                    result[field] = value.id
            else:
                result[field] = value

        return result

    def __getattr__(self, item):
        if item in self._related_fields:
            return getattr(self, f"one_to_one_{item}").lazy_load()
        return super().__getattribute__(item)
