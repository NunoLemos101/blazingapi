from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

from blazingapi.exceptions import BadRequestException, InternalServerErrorException


class BasePermission:
    """
    Base class for all permission classes.
    """
    def __call__(self, *args, **kwargs):
        raise NotImplementedError(".__call__() must be overridden.")


class HasHeader(BasePermission):
    """
    Allows access only if the request has the given header.
    """

    def __init__(self, header):
        self.header = header

    def __call__(self, request):
        if self.header not in request.headers:
            raise BadRequestException(f"Header {self.header} is required.")


class HasValidJSONSchema(BasePermission):
    """
    Allows access only if the request data matches the given JSON schema.
    """

    def __init__(self, schema):
        self.schema = schema

    def __call__(self, request):
        try:
            validate(instance=request.data, schema=self.schema)
        except ValidationError as e:
            raise BadRequestException(f"JSON schema validation error: {e.message}")
        except SchemaError as e:
            raise InternalServerErrorException(f"Invalid JSON schema: {e.message}")
