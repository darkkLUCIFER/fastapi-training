from src.core.choices import ChoiceEnum


__all__ = ('Permission',)


class Permission(ChoiceEnum):
    TODO_LIST_VIEW = 'todo-list.view'
    TODO_CREATE = 'todo.create'
    TODO_DETAIL = 'todo.detail'
    TODO_UPDATE = 'todo.update'
    TODO_DELETE = 'todo.delete'

    AUTH_TOKEN_REFRESH_VIEW = 'auth-token.refresh.view'
    AUTH_ME_VIEW = 'auth-me.view'
