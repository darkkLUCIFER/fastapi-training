"""set length for field description in model Todo

Revision ID: 3c9c746dc398
Revises: 46ecb98a3d7c
Create Date: 2026-07-05 22:32:03.521914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c9c746dc398'
down_revision: Union[str, Sequence[str], None] = '46ecb98a3d7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "todos",
        "description",
        existing_type=sa.String(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "todos",
        "description",
        existing_type=sa.String(length=500),
        type_=sa.String(),
        existing_nullable=True,
    )
