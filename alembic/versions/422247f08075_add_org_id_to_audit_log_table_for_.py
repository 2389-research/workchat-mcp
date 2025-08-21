"""Add org_id to audit_log table for organization isolation

Revision ID: 422247f08075
Revises: c4f007eb890f
Create Date: 2025-08-21 14:09:00.478432

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "422247f08075"
down_revision: Union[str, Sequence[str], None] = "c4f007eb890f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add org_id column to audit_log table
    op.add_column("audit_log", sa.Column("org_id", sa.String(length=32), nullable=True))

    # Add index for performance
    op.create_index(op.f("ix_audit_log_org_id"), "audit_log", ["org_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove index and column
    op.drop_index(op.f("ix_audit_log_org_id"), table_name="audit_log")
    op.drop_column("audit_log", "org_id")
