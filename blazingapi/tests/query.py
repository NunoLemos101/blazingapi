import unittest

from blazingapi.orm.query import Q


class TestQ(unittest.TestCase):

    def test_init(self):
        q = Q(id=1, name="test")
        self.assertEqual(q.query, {'id': 1, 'name': 'test'})
        self.assertEqual(q.connector, "AND")
        self.assertEqual(q.children, [])

    def test_add(self):
        q1 = Q(id=1)
        q2 = Q(name="test")
        q1.add(q2)
        self.assertEqual(len(q1.children), 1)
        self.assertEqual(q1.children[0], ("AND", q2))

    def test_or(self):
        q1 = Q(id=1)
        q2 = Q(name="test")
        q3 = q1 | q2
        self.assertEqual(q3.connector, "OR")
        self.assertEqual(len(q3.children), 2)
        self.assertEqual(q3.children[0], ("OR", q1))
        self.assertEqual(q3.children[1], ("OR", q2))

    def test_and(self):
        q1 = Q(id=1)
        q2 = Q(name="test")
        q3 = q1 & q2
        self.assertEqual(q3.connector, "AND")
        self.assertEqual(len(q3.children), 2)
        self.assertEqual(q3.children[0], ("AND", q1))
        self.assertEqual(q3.children[1], ("AND", q2))

    def test_get_sql_simple(self):
        q = Q(id=1, name="test")
        sql, values = q.get_sql()
        self.assertEqual(sql, '("id" = ? AND "name" = ?)')
        self.assertEqual(values, [1, "test"])

    def test_get_sql_with_in(self):
        q = Q(id__in=[1, 2, 3])
        sql, values = q.get_sql()
        self.assertEqual(sql, '("id" IN (?, ?, ?))')
        self.assertEqual(values, [1, 2, 3])

    def test_get_sql_complex(self):
        q1 = Q(id=1) & Q(name="test")
        q2 = Q(age=20)
        q3 = q1 | q2
        sql, values = q3.get_sql()
        self.assertEqual(sql, '((("id" = ?)) AND (("name" = ?))) OR (("age" = ?))')
        self.assertEqual(values, [1, "test", 20])

if __name__ == '__main__':
    unittest.main()