import sqlite3
import threading

from blazingapi.settings import settings


class ConnectionPool:
    _connections = threading.local()

    @classmethod
    def get_connection(cls):
        if not hasattr(cls._connections, 'conn'):
            cls._connections.conn = sqlite3.connect(settings.DB_FILE)
        return cls._connections.conn

    @classmethod
    def close_connection(cls):
        if hasattr(cls._connections, 'conn'):
            cls._connections.conn.close()
            del cls._connections.conn


class Manager:

    def __init__(self, model):
        self.model = model

    def all(self):
        connection = ConnectionPool.get_connection()
        cursor = connection.execute(f'SELECT * FROM users')
        rows = cursor.fetchall()
        instances = []

        # Get the list of column names from the cursor description
        columns = [col[0] for col in cursor.description]

        # Iterate over each row returned by the query
        for row in rows:
            # Zip together column names and row values to form a dictionary
            row_dict = dict(zip(columns, row))

            # Unpack the dictionary as keyword arguments to create an instance of the class
            instance = self.model(**row_dict)
            instances.append(instance)

        return instances

    def filter(self, **kwargs):
        connection = ConnectionPool.get_connection()

        fields = []
        values = []

        for key, value in kwargs.items():
            if key.endswith("__in"):
                field = key[:-4]
                if not isinstance(value, (list, tuple)):
                    raise ValueError(f"Expected a list or tuple for {field}__in filter, got {type(value).__name__}")
                placeholders = ', '.join(['?' for _ in value])
                fields.append(f'"{field}" IN ({placeholders})')
                values.extend(value)
            else:
                fields.append(f'"{key}" = ?')
                values.append(value)

        query = f'SELECT * FROM {self.model._table} WHERE {" AND ".join(fields)}'
        cursor = connection.execute(query, values)
        rows = cursor.fetchall()
        instances = []

        columns = [col[0] for col in cursor.description]

        for row in rows:
            row_dict = dict(zip(columns, row))
            instance = self.model(**row_dict)
            instances.append(instance)

        return instances

    def get(self, **kwargs):
        connection = ConnectionPool.get_connection()
        fields = [f'{key}=?' for key in kwargs.keys()]
        cursor = connection.execute(
            f'SELECT * FROM {self.model._table} WHERE {" AND ".join(fields)}',
            list(kwargs.values())
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self.model(**dict(zip([col[0] for col in cursor.description], row)))
