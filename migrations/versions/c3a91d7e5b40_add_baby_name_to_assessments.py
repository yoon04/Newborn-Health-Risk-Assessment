"""Add baby_name to assessments

Revision ID: c3a91d7e5b40
Revises: 8b7d9e4c1a2f
Create Date: 2026-08-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3a91d7e5b40'
down_revision = '8b7d9e4c1a2f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('assessments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('baby_name', sa.String(length=80), nullable=True))
        batch_op.create_index(batch_op.f('ix_assessments_baby_name'), ['baby_name'], unique=False)


def downgrade():
    with op.batch_alter_table('assessments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_assessments_baby_name'))
        batch_op.drop_column('baby_name')
