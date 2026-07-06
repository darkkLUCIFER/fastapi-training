__all__ = ('NotFoundError',)


class NotFoundError(Exception):
    def __init__(self, object_id: int, model_name: str):
        self.object_id = object_id
        super().__init__(f"{model_name} with id: {object_id} not found")
