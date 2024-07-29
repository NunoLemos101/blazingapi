from blazingapi.orm.fields import Field, PrimaryKeyField, ForeignKeyField
from blazingapi.orm.manager import Manager
from blazingapi.orm.query import ConnectionPool


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {key: attrs.pop(key) for key, value in list(attrs.items()) if isinstance(value, Field)}

        for base in bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)

        attrs['_fields'] = fields

        if '_table' not in attrs:
            attrs['_table'] = name.lower()

        new_class = super().__new__(cls, name, bases, attrs)
        new_class.manager = Manager(new_class)
        return new_class


class Model(metaclass=ModelMeta):

    _table = None
    serializable_fields = '__all__'
    id = PrimaryKeyField()

    def __init__(self, **kwargs):

        for field_name in kwargs:
            if field_name not in self._fields:
                raise AttributeError(f"Invalid field '{field_name}' for model '{self.__class__.__name__}'")

        for field_name in self._fields:
            setattr(self, field_name, kwargs.get(field_name))

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
        fields = ', '.join(self._fields.keys())
        values = ', '.join(['?'] * len(self._fields))
        cursor = connection.execute(
            f'INSERT INTO {self._table} ({fields}) VALUES ({values})',
            [getattr(self, field) for field in self._fields.keys()]
        )
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

        if self.serializable_fields == '__all__':
            return {field: getattr(self, field) for field in self._fields.keys()}

        return {field: getattr(self, field) for field in self.serializable_fields}
