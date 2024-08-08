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
