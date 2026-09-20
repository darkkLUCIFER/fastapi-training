from sqlalchemy import Text, String, Boolean, BigInteger, ForeignKey, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from src.core import Base
from src.auth.constants import RoleChoices
from src.auth.models.enums import user_role_enum
from src.core.database.mixins import TimestampMixin


__all__ = (
    'User',
    'Permission',
    'RolePermission',
)


class User(TimestampMixin, Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    role: Mapped[RoleChoices] = mapped_column(
        user_role_enum,
        nullable=False,
        default=RoleChoices.USER,
        server_default=RoleChoices.USER.value,
    )


class Permission(TimestampMixin, Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    key: Mapped[str] = mapped_column(String(length=100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)


class RolePermission(TimestampMixin, Base):
    __tablename__ = 'role_permissions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role: Mapped[RoleChoices] = mapped_column(
        user_role_enum,
        nullable=False,
        default=RoleChoices.USER,
        server_default=RoleChoices.USER.value,
    )
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    access: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)

    __table_args__ = (UniqueConstraint('role', 'permission_id', name='uq_role_permission'),)
