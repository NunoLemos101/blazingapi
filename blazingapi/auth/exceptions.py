from blazingapi.exceptions import APIException


class AuthenticationFailedException(APIException):
    status_code = 401
    default_detail = 'Authentication credentials were not provided or are invalid.'
    default_code = 'authentication_failed'


class PermissionDeniedException(APIException):
    status_code = 403
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'
