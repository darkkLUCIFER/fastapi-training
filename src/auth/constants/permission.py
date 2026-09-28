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

    PERMISSION_LIST_VIEW = 'auth.permission.list.view', _('auth.permission.list.view')
    PERMISSION_CREATE = 'auth.permission.create', _('auth.permission.create')
    PERMISSION_UPDATE = 'auth.permission.update', _('auth.permission.update')
    PERMISSION_DELETE = 'auth.permission.delete', _('auth.permission.delete')

    ROLE_PERMISSION_LIST_VIEW = 'auth.role-permission.list.view', _('auth.role-permission.list.view')
    ROLE_PERMISSION_CREATE = 'auth.role-permission.create', _('auth.role-permission.create')
    ROLE_PERMISSION_UPDATE = 'auth.role-permission.update', _('auth.role-permission.update')
    ROLE_PERMISSION_DETAIL = 'auth.role-permission.detail', _('auth.role-permission.detail')
