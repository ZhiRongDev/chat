"""add_email_verification_to_users

Revision ID: 927eedb46119
Revises: 001_gemini_file_search
Create Date: 2025-11-10 09:34:18.198974

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '927eedb46119'
down_revision = '001_gemini_file_search'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_verified column to user table with default value False
    op.add_column('user', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove is_verified column from user table
    op.drop_column('user', 'is_verified')
