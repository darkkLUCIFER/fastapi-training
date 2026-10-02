__all__ = (
    'NotFoundError',
    'NotMatchError',
    'ConflictError',
    'BadRequestError',
    'PermissionDenied',
)


class NotFoundError(Exception):
    def __init__(self, object_id: int, model_name: str):
        self.object_id = object_id
        self.model_name = model_name
        super().__init__(f'{model_name} with id: {object_id} not found')


class NotMatchError(Exception):
    def __init__(self):
        super().__init__('Input data does not match')


class ConflictError(Exception):
    """Raised when  write collides with existing state, e.g. a unique constraint."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class BadRequestError(Exception):
    """Raised when write is rejected because the submitted data is unusable."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class PermissionDenied(Exception):
    def __init__(self):
        super().__init__('Permission denied')
