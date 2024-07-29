import json

from enum import Enum
from typing import Dict, Union, Any, List

from blazingapi.orm.models import Model
from blazingapi.orm.query import QuerySet


class ResponseType(Enum):
    JSON = "application/json; charset=utf-8"
    HTML = "text/html; charset=utf-8"


class Response:
    def __init__(self, body: Union[str, Dict[str, Any], List[Any], Model, List[Model]], status: int = 200, headers: Dict[str, str] = None, content_type: ResponseType = ResponseType.JSON):
        self.body = body
        self.status = status
        self.headers = headers or {}
        self.content_type = content_type
        self.headers['Content-Type'] = content_type.value

    def to_http_response(self) -> Dict[str, Union[str, int, Dict[str, str]]]:
        if self.content_type == ResponseType.JSON:
            if isinstance(self.body, QuerySet):
                body_content = [model.serialize() for model in self.body.execute()]
            elif isinstance(self.body, List) and all(isinstance(item, Model) for item in self.body):
                body_content = [model.serialize() for model in self.body]
            elif isinstance(self.body, Model):
                body_content = self.body.serialize()
            else:
                body_content = self.body
            body_content = json.dumps(body_content)
        else:
            body_content = self.body

        result = {
            'body': body_content,
            'status_code': self.status,
            'headers': self.headers
        }
        return result

    def post_process(self, request) -> None:
        """
        Executes additional logic after the HTTP response has been sent.
        This method should be overridden by subclasses if post-processing is needed.
        """
        pass
