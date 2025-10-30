"""add_age_to_scores

Revision ID: 0878a2a8ac3b
Revises: 8c294a057c6c
Create Date: 2025-10-30 15:32:36.196747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0878a2a8ac3b'
down_revision: Union[str, None] = '8c294a057c6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('scores', sa.Column('age', sa.Integer()), schema='dekedata')
    op.create_index('ix_scores_player_age', 'scores', ['player_id', 'age'], schema='dekedata')


def downgrade() -> None:
    op.drop_index('ix_scores_player_age', table_name='scores', schema='dekedata')
    op.drop_column('scores', 'age', schema='dekedata')
