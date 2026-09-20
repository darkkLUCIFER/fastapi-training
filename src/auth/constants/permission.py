from gettext import gettext as _

from src.core.choices import ChoiceEnum


__all__ = ('PermissionChoices',)


class PermissionChoices(ChoiceEnum):
    TODO_LIST_VIEW = 'todo.list.view', _('todo.list.view')
    TODO_CREATE = 'todo.create', _('todo.create')
    TODO_DETAIL = 'todo.detail', _('todo.detail')
    TODO_UPDATE = 'todo.update', _('todo.update')
    TODO_DELETE = 'todo.delete', _('todo.delete')

    AUTH_TOKEN_REFRESH_VIEW = 'auth.token-refresh.view', _('auth.token-refresh.view')
    AUTH_ME_VIEW = 'auth.me.view', _('auth.me.view')
