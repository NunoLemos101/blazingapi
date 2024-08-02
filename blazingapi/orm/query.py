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


class Q:
    def __init__(self, **kwargs):
        self.query = kwargs
        self.connector = "AND"  # The default connector for conditions within this Q object
        self.children = []

    def add(self, q_object, connector=None):
        if not isinstance(q_object, Q):
            raise TypeError(f"Expected a Q object, got {type(q_object).__name__}")
        if connector is None:
            connector = self.connector
        self.children.append((connector, q_object))

    def __or__(self, other):
        if not isinstance(other, Q):
            raise TypeError(f"Expected Q object for | operation, got {type(other).__name__}")
        combined = Q()
        combined.connector = "OR"
        combined.add(self)
        combined.add(other, "OR")
        return combined

    def __and__(self, other):
        if not isinstance(other, Q):
            raise TypeError(f"Expected Q object for & operation, got {type(other).__name__}")
        combined = Q()
        combined.connector = "AND"
        combined.add(self)
        combined.add(other, "AND")
        return combined

    def get_sql(self):
        sql = []
        values = []

        for key, value in self.query.items():
            if key.endswith("__in"):
                field = key[:-4]
                placeholders = ', '.join(['?' for _ in value])
                sql.append(f'"{field}" IN ({placeholders})')
                values.extend(value)
            else:
                sql.append(f'"{key}" = ?')
                values.append(value)

        # Ensure internal conditions are grouped with the internal connector
        inner_sql = f" {self.connector} ".join(sql)
        if inner_sql:
            inner_sql = f"({inner_sql})"

        # Now handle the children which are combined with connectors (AND/OR)
        for connector, child in self.children:
            child_sql, child_values = child.get_sql()
            if inner_sql:
                inner_sql += f" {connector} ({child_sql})"
            else:
                inner_sql = f"({child_sql})"
            values.extend(child_values)

        return inner_sql, values


class QuerySet:

    def __init__(self, model):
        self.model = model
        self.q_obj = None
        self.limit = None
        self.offset = None
        self.cache = None
        self._limit = None
        self._offset = None

    def all(self):
        return self

    def filter(self, *args, **kwargs):
        if kwargs:
            q = Q(**kwargs)
            if self.q_obj:
                self.q_obj = self.q_obj & q
            else:
                self.q_obj = q

        if args:
            arg_query = args[0]
            if not isinstance(arg_query, Q):
                raise ValueError(f"Expected Q object, got {type(arg_query).__name__}")
            if self.q_obj:
                self.q_obj &= arg_query
            else:
                self.q_obj = arg_query

        return self

    def get(self):
        connection = ConnectionPool.get_connection()
        if self.q_obj is None:
            raise ValueError("get() must be called with at least one filtering condition.")

        where_clause, values = self.q_obj.get_sql()
        query = f'SELECT * FROM {self.model._table} WHERE {where_clause}'
        cursor = connection.execute(query, values)
        row = cursor.fetchone()
        print(f'SELECT * FROM {self.model._table} WHERE {where_clause}', values)
        if row is None:
            return None

        columns = [col[0] for col in cursor.description]
        return self.model(**dict(zip(columns, row)))

    def execute(self):
        self._exec_query()
        return iter(self.cache)

    def _exec_query(self):
        if self.cache is None:
            connection = ConnectionPool.get_connection()
            if self.q_obj is None:
                query = f'SELECT * FROM {self.model._table}'
                values = []
            else:
                where_clause, values = self.q_obj.get_sql()
                query = f'SELECT * FROM {self.model._table} WHERE {where_clause}'

            if self._limit is not None:
                query += f' LIMIT {self._limit}'

            if self._offset is not None:
                query += f' OFFSET {self._offset}'
            print(query, values)
            cursor = connection.execute(query, values)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            instances = [self.model(**dict(zip(columns, row))) for row in rows]
            self.cache = instances
            return instances
        return self.cache

    def __getitem__(self, key):
        """
        Applies LIMIT and OFFSET to the query.

        Also handles indexing for QuerySet instances.
        """
        if isinstance(key, slice):
            if key.stop and key.start is None:
                self._limit = key.stop
                self._offset = None
            else:
                self._limit = key.stop - key.start if key.stop is not None else None
                self._offset = key.start
            return self
        elif isinstance(key, int):
            self._exec_query()
            return self.cache[key]
        raise TypeError("Invalid argument type.")

    def __iter__(self):
        """
        Evaluates the query and returns an iterator over the results.
        """
        self._exec_query()
        return iter(self.cache)

    def __len__(self):
        """
        Evaluates the query and returns the number of results
        """
        self._exec_query()
        return len(self.cache)
