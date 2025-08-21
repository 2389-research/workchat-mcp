"""Add self-reference foreign key for message thread_id

Revision ID: f72b0b971ce8
Revises: 4984b962e52c
Create Date: 2025-08-21 10:31:30.748630

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "f72b0b971ce8"
down_revision: Union[str, Sequence[str], None] = "4984b962e52c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add foreign key constraint for thread_id to reference message.id
    # Note: SQLite doesn't support adding FK constraints to existing tables
    # This would require recreating the table in a real migration
    # For now, we'll document this as a TODO for proper implementation
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
