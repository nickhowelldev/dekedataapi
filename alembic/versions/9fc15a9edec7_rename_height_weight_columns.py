"""rename_height_weight_columns

Revision ID: 9fc15a9edec7
Revises: 3862cc265948
Create Date: 2025-10-30 14:01:38.598451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fc15a9edec7'
down_revision: Union[str, None] = '3862cc265948'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename height_cm to height
    op.alter_column('players', 'height_cm',
                    new_column_name='height',
                    schema='dekedata')

    # Rename weight_kg to weight
    op.alter_column('players', 'weight_kg',
                    new_column_name='weight',
                    schema='dekedata')

    # Drop the raw columns
    op.drop_column('players', 'height_raw', schema='dekedata')
    op.drop_column('players', 'weight_raw', schema='dekedata')


def downgrade() -> None:
    # Add back raw columns
    op.add_column('players', sa.Column('height_raw', sa.Text(), nullable=True), schema='dekedata')
    op.add_column('players', sa.Column('weight_raw', sa.Text(), nullable=True), schema='dekedata')

    # Rename back
    op.alter_column('players', 'height',
                    new_column_name='height_cm',
                    schema='dekedata')

    op.alter_column('players', 'weight',
                    new_column_name='weight_kg',
                    schema='dekedata')
