from sqlalchemy.dialects.postgresql import ENUM

from src.auth.constants import RoleChoices


__all__ = ('user_role_enum',)

user_role_enum = ENUM(RoleChoices, name='user_role', values_callable=lambda x: [e.value for e in x], create_type=False)
