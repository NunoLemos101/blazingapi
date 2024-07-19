import json
import unittest

from framework.response import Response, ResponseType


class TestResponse(unittest.TestCase):
    def test_to_http_response_json_dict(self):
        body = {"key": "value"}
        response = Response(body=body, content_type=ResponseType.JSON)
        http_response = response.to_http_response()

        expected_http_response = {
            'body': json.dumps(body),
            'status_code': 200,
            'headers': {'Content-Type': "application/json; charset=utf-8"}
        }

        self.assertEqual(http_response, expected_http_response)

    def test_to_http_response_json_list(self):
        body = ["item1", "item2"]
        response = Response(body=body, content_type=ResponseType.JSON)
        http_response = response.to_http_response()

        expected_http_response = {
            'body': json.dumps(body),
            'status_code': 200,
            'headers': {'Content-Type': "application/json; charset=utf-8"}
        }

        self.assertEqual(http_response, expected_http_response)

    def test_to_http_response_html(self):
        body = "<html><body>Hello, World!</body></html>"
        response = Response(body=body, content_type=ResponseType.HTML)
        http_response = response.to_http_response()

        expected_http_response = {
            'body': body,
            'status_code': 200,
            'headers': {'Content-Type': "text/html; charset=utf-8"}
        }

        self.assertEqual(http_response, expected_http_response)

    def test_custom_headers(self):
        body = {"key": "value"}
        custom_headers = {"X-Custom-Header": "CustomValue"}
        response = Response(body=body, headers=custom_headers, content_type=ResponseType.JSON)
        http_response = response.to_http_response()

        expected_http_response = {
            'body': json.dumps(body),
            'status_code': 200,
            'headers': {'Content-Type': "application/json; charset=utf-8", "X-Custom-Header": "CustomValue"}
        }

        self.assertEqual(http_response, expected_http_response)

    def test_post_process_override(self):
        class CustomResponse(Response):
            def post_process(self, request):
                self.processed = True

        response = CustomResponse(body={"message": "Test"}, content_type=ResponseType.JSON)
        response.post_process(None)  # Pass None for request because it's not used
        self.assertTrue(hasattr(response, 'processed'))
        self.assertTrue(response.processed)


if __name__ == '__main__':
    unittest.main()
