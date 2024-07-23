import json
from typing import Dict, Optional, Union, List, Any


class Request:
    def __init__(self, path: str, method: str, headers: Dict[str, str], body: bytes):
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
        self.data = self._parse_body(body)

    def _parse_body(self, body: bytes) -> Optional[Union[Dict[str, Any], List[Any]]]:
        content_type = self.headers.get('Content-Type', '')
        if 'application/json' in content_type and body:
            try:
                return json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON")
        return None

    @classmethod
    def from_environ(cls, environ):
        # Extract the necessary information from the environ dictionary
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']
        headers = {k: v for k, v in environ.items() if k.startswith('HTTP_')}
        headers['Content-Type'] = environ.get('CONTENT_TYPE', 'application/json')
        body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0)))

        # Create and return a Request object
        return cls(path=path, method=method, headers=headers, body=body)
