from gettext import gettext as _
from src.core.choices import ChoiceEnum


__all__ = ("RoleChoices",)


class RoleChoices(ChoiceEnum):
    ADMIN = "admin", _("admin")
    USER = "user", _("user")
