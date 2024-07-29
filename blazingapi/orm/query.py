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