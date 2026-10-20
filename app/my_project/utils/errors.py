"""HTTP-friendly application errors."""


class ApiError(Exception):
    status_code = 400
    error_code = "bad_request"

    def __init__(self, message: str, status_code: int | None = None, error_code: str | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code


class ValidationError(ApiError):
    status_code = 400
    error_code = "validation_error"


class NotFoundError(ApiError):
    status_code = 404
    error_code = "not_found"


class ConflictError(ApiError):
    status_code = 409
    error_code = "data_conflict"
