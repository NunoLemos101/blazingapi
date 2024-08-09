import sys
import traceback

from blazingapi.settings import settings


class APIException(Exception):
    status_code = 500
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail

        if status_code is not None:
            self.status_code = status_code

        super().__init__(self.detail)

    def serialize(self):
        result = {
            "code": self.default_code,
            "detail": self.detail
        }

        if settings.DEBUG:
            result["traceback"] = self._get_traceback()

        return result

    def _get_traceback(self):
        exc_type, exc_value, tb = sys.exc_info()
        tb_list = traceback.format_exception(exc_type, exc_value, tb)
        return tb_list


class NotFoundException(APIException):
    status_code = 404
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'


class BadRequestException(APIException):
    status_code = 400
    default_detail = 'The request could not be understood or was missing required parameters.'
    default_code = 'bad_request'


class InternalServerErrorException(APIException):
    status_code = 500
    default_detail = 'An internal server error occurred.'
    default_code = 'internal_server_error'


class ServiceUnavailableException(APIException):
    status_code = 503
    default_detail = 'The service is temporarily unavailable. Please try again later.'
    default_code = 'service_unavailable'

