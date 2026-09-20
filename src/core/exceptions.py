__all__ = (
    'NotFoundError',
    'NotMatchError',
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


class PermissionDenied(Exception):
    def __init__(self):
        super().__init__('Permission denied')
