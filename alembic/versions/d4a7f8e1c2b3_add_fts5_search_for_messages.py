"""Add FTS5 search for messages

Revision ID: d4a7f8e1c2b3
Revises: c858cce272e8
Create Date: 2025-08-20 14:45:30.123456

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4a7f8e1c2b3"
down_revision: Union[str, Sequence[str], None] = "c858cce272e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable FTS5 extension (SQLite should have it by default)
    # Create FTS5 virtual table for message search
    op.execute(
        """
        CREATE VIRTUAL TABLE message_fts USING fts5(
            message_id UNINDEXED,
            channel_id UNINDEXED,
            body,
            content='message',
            content_rowid='id'
        )
    """
    )

    # Create triggers to keep FTS table in sync with message table
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

    # Populate existing messages into FTS table
    op.execute(
        """
        INSERT INTO message_fts(message_id, channel_id, body)
        SELECT id, channel_id, body FROM message
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS message_fts_delete")
    op.execute("DROP TRIGGER IF EXISTS message_fts_update")
    op.execute("DROP TRIGGER IF EXISTS message_fts_insert")

    # Drop FTS table
    op.execute("DROP TABLE IF EXISTS message_fts")
