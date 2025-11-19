"""add_trigram_indexes_for_fuzzy_search

Revision ID: 88f333f28d69
Revises: 0878a2a8ac3b
Create Date: 2025-11-19 16:40:43.102170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88f333f28d69'
down_revision: Union[str, None] = '0878a2a8ac3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_players_name_trgm
        ON dekedata.players
        USING gin (name gin_trgm_ops)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_players_name_lower_btree
        ON dekedata.players
        USING btree (LOWER(name))
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS dekedata.idx_players_name_lower_btree")
    op.execute("DROP INDEX IF EXISTS dekedata.idx_players_name_trgm")
