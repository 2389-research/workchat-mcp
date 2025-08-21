"""Temporarily disable FTS triggers

Revision ID: 4984b962e52c
Revises: d4a7f8e1c2b3
Create Date: 2025-08-21 10:27:39.600861

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4984b962e52c"
down_revision: Union[str, Sequence[str], None] = "d4a7f8e1c2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Disable FTS triggers temporarily to fix message operations
    op.execute("DROP TRIGGER IF EXISTS message_fts_delete")
    op.execute("DROP TRIGGER IF EXISTS message_fts_update")
    op.execute("DROP TRIGGER IF EXISTS message_fts_insert")


def downgrade() -> None:
    """Downgrade schema."""
    # Re-enable FTS triggers
    op.execute(
        """
        CREATE TRIGGER message_fts_insert AFTER INSERT ON message
        BEGIN
            INSERT INTO message_fts(message_id, channel_id, body)
            VALUES (new.id, new.channel_id, new.body);
        END
    """
    )

    op.execute(
        """
        CREATE TRIGGER message_fts_update AFTER UPDATE ON message
        BEGIN
            DELETE FROM message_fts WHERE message_id = old.id;
            INSERT INTO message_fts(message_id, channel_id, body)
            VALUES (new.id, new.channel_id, new.body);
        END
    """
    )

    op.execute(
        """
        CREATE TRIGGER message_fts_delete AFTER DELETE ON message
        BEGIN
            DELETE FROM message_fts WHERE message_id = old.id;
        END
    """
    )
