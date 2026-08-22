"""Add password hashes and unique registered-user emails.

Revision ID: 8b7d9e4c1a2f
Revises: f45fb29a99ea
"""

from alembic import op
import sqlalchemy as sa


revision = '8b7d9e4c1a2f'
down_revision = 'f45fb29a99ea'
branch_labels = None
depends_on = None


def upgrade():
    # Nullable preserves users created by the pre-authentication form. New
    # registrations always write a Werkzeug password hash.
    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(length=255), nullable=True),
    )
    op.drop_index('ix_users_email', table_name='users')
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade():
    op.drop_index('ix_users_email', table_name='users')
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.drop_column('users', 'password_hash')
