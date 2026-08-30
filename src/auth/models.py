from sqlalchemy import Enum, String, Boolean, BigInteger, true
from sqlalchemy.orm import Mapped, mapped_column

from src.core import Base
from src.auth.constants import RoleChoices
from src.core.database.mixins import TimestampMixin


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
        Enum(
            RoleChoices,
            name='user_role',
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=RoleChoices.USER,
        server_default=RoleChoices.USER.value,
    )
