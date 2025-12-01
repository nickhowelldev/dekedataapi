"""create_player_lists_table

Revision ID: 4c9ed6ee1192
Revises: 88f333f28d69
Create Date: 2025-12-01 13:03:56.139522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c9ed6ee1192'
down_revision: Union[str, None] = '88f333f28d69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE player_lists (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            player_ids UUID[] NOT NULL DEFAULT '{}',
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    op.execute("""
        CREATE INDEX idx_player_lists_user_id ON player_lists(user_id)
    """)

    op.execute("""
        CREATE INDEX idx_player_lists_created_at ON player_lists(created_at DESC)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_player_lists_created_at")
    op.execute("DROP INDEX IF EXISTS idx_player_lists_user_id")
    op.execute("DROP TABLE IF EXISTS player_lists")
