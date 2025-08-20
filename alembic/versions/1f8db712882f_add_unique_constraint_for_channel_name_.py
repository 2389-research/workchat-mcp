"""Add unique constraint for channel name per org

Revision ID: 1f8db712882f
Revises: b8e0715eeaba
Create Date: 2025-08-20 13:08:20.032953

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f8db712882f"
down_revision: Union[str, Sequence[str], None] = "b8e0715eeaba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite requires batch mode to add constraints to existing tables
    with op.batch_alter_table("channel") as batch_op:
        batch_op.create_unique_constraint("uq_channel_name_per_org", ["org_id", "name"])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the unique constraint using batch mode
    with op.batch_alter_table("channel") as batch_op:
        batch_op.drop_constraint("uq_channel_name_per_org", type_="unique")
