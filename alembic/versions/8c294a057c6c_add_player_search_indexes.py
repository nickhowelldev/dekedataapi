"""add_player_search_indexes

Revision ID: 8c294a057c6c
Revises: 9fc15a9edec7
Create Date: 2025-10-30 14:14:03.974265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c294a057c6c'
down_revision: Union[str, None] = '9fc15a9edec7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add indexes for faster player searches

    # Index on name for ILIKE queries (case-insensitive search)
    # Using gin with pg_trgm for fuzzy search would be even better
    op.create_index(
        'ix_players_name_lower',
        'players',
        [sa.text('LOWER(name)')],
        schema='dekedata'
    )

    # Index on position (already fast, but explicit index helps)
    op.create_index(
        'ix_players_position',
        'players',
        ['position'],
        schema='dekedata'
    )

    # Index on birth_year for age-based searches
    op.create_index(
        'ix_players_birth_year',
        'players',
        ['birth_year'],
        schema='dekedata'
    )

    # Composite index for common filter combinations
    op.create_index(
        'ix_players_position_birth_year',
        'players',
        ['position', 'birth_year'],
        schema='dekedata'
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_players_position_birth_year', table_name='players', schema='dekedata')
    op.drop_index('ix_players_birth_year', table_name='players', schema='dekedata')
    op.drop_index('ix_players_position', table_name='players', schema='dekedata')
    op.drop_index('ix_players_name_lower', table_name='players', schema='dekedata')
