"""Add authentication fields to user table

Revision ID: 7caaf6dd0cce
Revises: f7298981ad16
Create Date: 2025-08-19 15:14:53.898474

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7caaf6dd0cce"
down_revision: Union[str, Sequence[str], None] = "f7298981ad16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add authentication fields to existing user table
    op.add_column(
        "user",
        sa.Column(
            "hashed_password",
            sa.String(),
            nullable=False,
            server_default="$2b$12$invalid.hash.placeholder.for.migration",
        ),
    )
    op.add_column(
        "user", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1")
    )
    op.add_column(
        "user",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "user",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove authentication fields from user table
    op.drop_column("user", "is_verified")
    op.drop_column("user", "is_superuser")
    op.drop_column("user", "is_active")
    op.drop_column("user", "hashed_password")
