import json
import unittest

from framework.request import Request


class TestRequest(unittest.TestCase):
    def test_parse_json_body_dict(self):
        path = "/test"
        method = "POST"
        headers = {"Content-Type": "application/json"}
        body_dict = {"key": "value"}
        body = json.dumps(body_dict).encode('utf-8')

        request = Request(path, method, headers, body)
        self.assertEqual(request.data, body_dict)
        self.assertEqual(request.body, body)

    def test_parse_json_body_list(self):
        path = "/test"
        method = "POST"
        headers = {"Content-Type": "application/json"}
        body_list = ["item1", "item2"]
        body = json.dumps(body_list).encode('utf-8')

        request = Request(path, method, headers, body)
        self.assertEqual(request.data, body_list)
        self.assertEqual(request.body, body)

    def test_non_json_content_type(self):
        path = "/test"
        method = "GET"
        headers = {"Content-Type": "text/plain"}
        body = b"Simple text."

        request = Request(path, method, headers, body)
        self.assertIsNone(request.data)
        self.assertEqual(request.body, body)

    def test_invalid_json(self):
        path = "/test"
        method = "POST"
        headers = {"Content-Type": "application/json"}
        body = b"invalid json"

        with self.assertRaises(ValueError) as context:
            Request(path, method, headers, body)

        self.assertEqual(str(context.exception), "Invalid JSON")

    def test_empty_body(self):
        path = "/test"
        method = "GET"
        headers = {"Content-Type": "application/json"}
        body = b""

        request = Request(path, method, headers, body)
        self.assertIsNone(request.data)
        self.assertEqual(request.body, body)

    def test_missing_content_type(self):
        path = "/test"
        method = "POST"
        headers = {}
        body_dict = {"key": "value"}
        body = json.dumps(body_dict).encode('utf-8')

        request = Request(path, method, headers, body)
        self.assertIsNone(request.data)
        self.assertEqual(request.body, body)


if __name__ == '__main__':
    unittest.main()
