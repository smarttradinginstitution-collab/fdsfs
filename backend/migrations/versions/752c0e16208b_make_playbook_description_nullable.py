"""make_playbook_description_nullable

Revision ID: 752c0e16208b
Revises:
Create Date: 2025-11-26 16:24:31.786701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '752c0e16208b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('playbooks', 'description',
               existing_type=sa.TEXT(),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('playbooks', 'description',
               existing_type=sa.TEXT(),
               nullable=False)
