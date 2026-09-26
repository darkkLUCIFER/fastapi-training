from gettext import gettext as _

from src.core.choices import ChoiceEnum


__all__ = ('PermissionChoices',)


class PermissionChoices(ChoiceEnum):
    TODO_LIST_VIEW = 'todo.list.view', _('todo.list.view')
    TODO_CREATE = 'todo.create', _('todo.create')
    TODO_DETAIL = 'todo.detail.view', _('todo.detail.view')
    TODO_UPDATE = 'todo.update', _('todo.update')
    TODO_DELETE = 'todo.delete', _('todo.delete')

    AUTH_TOKEN_REFRESH_VIEW = 'auth.token-refresh.view', _('auth.token-refresh.view')
    AUTH_ME_VIEW = 'auth.me.view', _('auth.me.view')

    PERMISSION_LIST_VIEW = 'permission.list.view', _('permission.list.view')
    PERMISSION_CREATE = 'permission.create', _('permission.create')
    PERMISSION_UPDATE = 'permission.update', _('permission.update')
    PERMISSION_DELETE = 'permission.delete', _('permission.delete')
