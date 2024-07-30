from blazingapi.orm.fields import Field, PrimaryKeyField, ForeignKeyField
from blazingapi.orm.manager import Manager
from blazingapi.orm.query import ConnectionPool


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
            if field_name in self._foreign_keys:
                if isinstance(value, Model):
                    setattr(self, field_name, value)
                else:
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

        connection.execute(f'CREATE TABLE IF NOT EXISTS {cls._table} ({fields_str})')
        print("Table created if not exists: ", cls._table)

    def save(self):
        connection = ConnectionPool.get_connection()

        fields = []
        values = []

        for field in self._fields:
            value = getattr(self, field)
            fields.append(field)
            if isinstance(value, Model):
                if value.id is None:
                    value.save()
                values.append(getattr(value, "id"))
            else:
                values.append(getattr(self, field))

        field_str = ', '.join(fields)
        placeholder_str = ', '.join(['?'] * len(fields))

        sql_statement = f'INSERT INTO {self._table} ({field_str}) VALUES ({placeholder_str})'
        cursor = connection.execute(sql_statement, values)

        self.id = cursor.lastrowid
        connection.commit()

    def update(self, **kwargs):
        connection = ConnectionPool.get_connection()
        fields = ', '.join([f'{key}=?' for key in kwargs.keys()])
        cursor = self._get_connection().execute(
            f'UPDATE {self._table} SET {fields} WHERE id=?',
            list(kwargs.values()) + [self.id]
        )
        connection.commit()

    def delete(self):
        connection = ConnectionPool.get_connection()
        cursor = connection.execute(
            f'DELETE FROM {self._table} WHERE id=?',
            (self.id, )
        )
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
