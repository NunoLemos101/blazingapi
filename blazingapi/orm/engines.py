import sqlite3
import threading
from queue import Queue, Empty

import psycopg2
import mysql.connector

from blazingapi.settings import settings


class ConnectionPool:
    _connections = threading.local()
    _pool_size = 5
    _connection_queue = Queue(maxsize=_pool_size)

    @classmethod
    def create_pool(cls, engine):
        for _ in range(cls._pool_size):
            conn = engine.get_connection()
            cls._connection_queue.put(conn)

    @classmethod
    def get_connection(cls, engine):
        if not hasattr(cls._connections, 'conn'):
            try:
                cls._connections.conn = cls._connection_queue.get_nowait()
                return cls._connections.conn
            except Empty:
                # Create a new connection if the pool is empty (fallback)
                print('Creating new connection as pool is empty.')
                cls._connections.conn = engine.get_connection()
                return cls._connections.conn
        return cls._connections.conn

    @classmethod
    def close_connection(cls):
        if hasattr(cls._connections, 'conn'):
            # Put the connection back into the pool instead of closing it
            cls._connection_queue.put(cls._connections.conn)
            del cls._connections.conn


class BaseEngine:

    def get_sql(self, q_obj):
        raise NotImplementedError("Subclasses must implement this method")

    def render_field_sql(self, field, column):
        raise NotImplementedError("Subclasses must implement this method")

    def render_foreign_key_field_sql(self, field, column):
        raise NotImplementedError("Subclasses must implement this method")

    def generate_insert_statement(self, table, fields, values):
        raise NotImplementedError("Subclasses must implement this method")

    def get_connection(self):
        raise NotImplementedError("Subclasses must implement this method")


class SQLiteEngine(BaseEngine):

    placeholder = "?"

    data_types = {
        "IntegerField": "INTEGER",
        "TextField": "TEXT",
        "VarCharField": "VARCHAR(%(max_length)s)",
        "EmailField": "VARCHAR(256)",
        "PrimaryKeyField": "INTEGER PRIMARY KEY",
        "ForeignKeyField": "INTEGER",
        "OneToOneField": "INTEGER",
        "PositiveIntegerField": "INTEGER",
        "NegativeIntegerField": "INTEGER",
        "NonPositiveIntegerField": "INTEGER",
        "NonNegativeIntegerField": "INTEGER",
        "FloatField": "REAL",
        "PositiveFloatField": "REAL",
        "NegativeFloatField": "REAL",
        "NonPositiveFloatField": "REAL",
        "NonNegativeFloatField": "REAL",
        "DateTimeField": "DATETIME",
    }

    def get_sql(self, q_obj):
        sql = []
        values = []

        for key, value in q_obj.query.items():
            if key.endswith("__in"):
                field = key[:-4]
                placeholders = ', '.join([self.placeholder for _ in value])
                sql.append(f'"{field}" IN ({placeholders})')
                values.extend(value)
            else:
                sql.append(f'"{key}" = {self.placeholder}')
                values.append(value)

        inner_sql = f" {q_obj.connector} ".join(sql)
        if inner_sql:
            inner_sql = f"({inner_sql})"

        for connector, child in q_obj.children:
            child_sql, child_values = child.get_sql()
            if inner_sql:
                inner_sql += f" {connector} ({child_sql})"
            else:
                inner_sql = f"({child_sql})"
            values.extend(child_values)

        return inner_sql, values

    def render_field_sql(self, field, column):
        null_constraint = "" if field.nullable else " NOT NULL"
        unique_constraint = " UNIQUE" if field.unique else ""

        if field.default is None or callable(field.default):
            default_constraint = ""
        elif isinstance(field.default, str):
            default_constraint = f' DEFAULT "{field.default}"'
        else:
            default_constraint = f' DEFAULT {field.default}'

        data_type = self.data_types[field.__class__.__name__]

        if field.__class__.__name__ == "VarCharField":
            data_type = data_type % {'max_length': field.max_length}

        return f'"{column}" {data_type}{null_constraint}{unique_constraint}{default_constraint}'

    def render_foreign_key_field_sql(self, field, column):
        if field.reference_model is str:
            reference_table = field.reference_model
        else:
            reference_table = field.reference_model._table

        reference_field = 'id'
        return f'FOREIGN KEY("{column}") REFERENCES "{reference_table}" ("{reference_field}") ON DELETE {field.on_delete.value} ON UPDATE {field.on_update.value}'

    def generate_insert_statement(self, table, fields, values):
        field_str = ', '.join(fields)
        placeholder_str = ', '.join([self.placeholder] * len(fields))
        sql_statement = f'INSERT INTO {table} ({field_str}) VALUES ({placeholder_str})'
        return sql_statement, values

    def get_connection(self):
        return sqlite3.connect(settings.DB_CONNECTION["database"])


class PostgreSQLEngine(BaseEngine):

    placeholder = "%s"

    data_types = {
        "IntegerField": "INTEGER",
        "TextField": "TEXT",
        "VarCharField": "VARCHAR(%(max_length)s)",
        "EmailField": "VARCHAR(256)",
        "PrimaryKeyField": "SERIAL PRIMARY KEY",
        "ForeignKeyField": "INTEGER",
        "OneToOneField": "INTEGER",
        "PositiveIntegerField": "INTEGER",
        "NegativeIntegerField": "INTEGER",
        "NonPositiveIntegerField": "INTEGER",
        "NonNegativeIntegerField": "INTEGER",
        "FloatField": "REAL",
        "PositiveFloatField": "REAL",
        "NegativeFloatField": "REAL",
        "NonPositiveFloatField": "REAL",
        "NonNegativeFloatField": "REAL",
        "DateTimeField": "TIMESTAMP",
    }

    def get_sql(self, q_obj):
        sql = []
        values = []

        for key, value in q_obj.query.items():
            if key.endswith("__in"):
                field = key[:-4]
                placeholders = ', '.join([self.placeholder for _ in value])
                sql.append(f'"{field}" IN ({placeholders})')
                values.extend(value)
            else:
                sql.append(f'"{key}" = {self.placeholder}')
                values.append(value)

        inner_sql = f" {q_obj.connector} ".join(sql)
        if inner_sql:
            inner_sql = f"({inner_sql})"

        for connector, child in q_obj.children:
            child_sql, child_values = child.get_sql()
            if inner_sql:
                inner_sql += f" {connector} ({child_sql})"
            else:
                inner_sql = f"({child_sql})"
            values.extend(child_values)

        return inner_sql, values

    def render_field_sql(self, field, column):
        null_constraint = "" if field.nullable else " NOT NULL"
        unique_constraint = " UNIQUE" if field.unique else ""

        if field.default is None or callable(field.default):
            default_constraint = ""
        elif isinstance(field.default, str):
            default_constraint = f' DEFAULT "{field.default}"'
        else:
            default_constraint = f' DEFAULT {field.default}'

        data_type = self.data_types[field.__class__.__name__]

        if field.__class__.__name__ == "VarCharField":
            data_type = data_type % {'max_length': field.max_length}

        return f'"{column}" {data_type}{null_constraint}{unique_constraint}{default_constraint}'

    def render_foreign_key_field_sql(self, field, column):
        if field.reference_model is str:
            reference_table = field.reference_model
        else:
            reference_table = field.reference_model._table

        reference_field = 'id'
        return f'FOREIGN KEY("{column}") REFERENCES "{reference_table}" ("{reference_field}") ON DELETE {field.on_delete.value} ON UPDATE {field.on_update.value}'

    def generate_insert_statement(self, table, fields, values):
        #  In PostgresSQL the field "user" is a reserved keyword and must be quoted.
        if "user" in fields:
            fields[fields.index("user")] = '"user"'
        #  While in SQLite database we can pass the id column as None and the autoincrement will work.
        #  In PostgresSQL we need to remove the id field from the fields and values list.
        if "id" in fields:
            id_index = fields.index("id")
            fields.pop(id_index)
            values.pop(id_index)
        field_str = ', '.join(fields)
        placeholder_str = ', '.join([self.placeholder] * len(fields))
        sql_statement = f'INSERT INTO {table} ({field_str}) VALUES ({placeholder_str})'
        return sql_statement, values

    def get_connection(self):
        return psycopg2.connect(
            dbname=settings.DB_CONNECTION["database"],
            user=settings.DB_CONNECTION["user"],
            password=settings.DB_CONNECTION["password"],
            host=settings.DB_CONNECTION["host"],
            port=settings.DB_CONNECTION["port"],
        )


class MySQLEngine(BaseEngine):

    placeholder = "%s"

    data_types = {
        "IntegerField": "INT",
        "TextField": "TEXT",
        "VarCharField": "VARCHAR(%(max_length)s)",
        "EmailField": "VARCHAR(256)",
        "PrimaryKeyField": "INT PRIMARY KEY AUTO_INCREMENT",
        "ForeignKeyField": "INT",
        "OneToOneField": "INT",
        "PositiveIntegerField": "INT",
        "NegativeIntegerField": "INT",
        "NonPositiveIntegerField": "INT",
        "NonNegativeIntegerField": "INT",
        "FloatField": "FLOAT",
        "PositiveFloatField": "FLOAT",
        "NegativeFloatField": "FLOAT",
        "NonPositiveFloatField": "FLOAT",
        "NonNegativeFloatField": "FLOAT",
        "DateTimeField": "DATETIME",
    }

    def get_sql(self, q_obj):
        sql = []
        values = []

        for key, value in q_obj.query.items():
            if key.endswith("__in"):
                field = key[:-4]
                placeholders = ', '.join([self.placeholder for _ in value])
                sql.append(f'`{field}` IN ({placeholders})')
                values.extend(value)
            else:
                sql.append(f'`{key}` = {self.placeholder}')
                values.append(value)

        inner_sql = f" {q_obj.connector} ".join(sql)
        if inner_sql:
            inner_sql = f"({inner_sql})"

        for connector, child in q_obj.children:
            child_sql, child_values = child.get_sql()
            if inner_sql:
                inner_sql += f" {connector} ({child_sql})"
            else:
                inner_sql = f"({child_sql})"
            values.extend(child_values)

        return inner_sql, values

    def render_field_sql(self, field, column):
        null_constraint = "" if field.nullable else " NOT NULL"
        unique_constraint = " UNIQUE" if field.unique else ""

        if field.default is None or callable(field.default):
            default_constraint = ""
        elif isinstance(field.default, str):
            default_constraint = f" DEFAULT '{field.default}'"
        else:
            default_constraint = f' DEFAULT {field.default}'

        data_type = self.data_types[field.__class__.__name__]

        if field.__class__.__name__ == "VarCharField":
            data_type = data_type % {'max_length': field.max_length}

        return f"`{column}` {data_type}{null_constraint}{unique_constraint}{default_constraint}"

    def render_foreign_key_field_sql(self, field, column):
        if field.reference_model is str:
            reference_table = field.reference_model
        else:
            reference_table = field.reference_model._table

        reference_field = 'id'
        return f'FOREIGN KEY(`{column}`) REFERENCES `{reference_table}` (`{reference_field}`) ON DELETE {field.on_delete.value} ON UPDATE {field.on_update.value}'

    def generate_insert_statement(self, table, fields, values):
        field_str = ', '.join(fields)
        placeholder_str = ', '.join([self.placeholder] * len(fields))
        sql_statement = f'INSERT INTO {table} ({field_str}) VALUES ({placeholder_str})'
        return sql_statement, values

    def get_connection(self):
        return mysql.connector.connect(
            host=settings.DB_CONNECTION["host"],
            port=settings.DB_CONNECTION["port"],
            user=settings.DB_CONNECTION["user"],
            password=settings.DB_CONNECTION["password"],
            database=settings.DB_CONNECTION["database"],
        )
