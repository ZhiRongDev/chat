"""Add api_key_hash to gemini_file_search_store

Revision ID: 002_api_key_hash
Revises: 001_gemini_file_search
Create Date: 2025-01-09

This migration adds api_key_hash field to gemini_file_search_store table
to support multiple API keys per user.

"""
from alembic import op
import sqlalchemy as sa
import hashlib

# revision identifiers, used by Alembic.
revision = '002_api_key_hash'
down_revision = '927eedb46119'  # Depends on email verification migration
branch_labels = None
depends_on = None


def upgrade():
    """Add api_key_hash column to gemini_file_search_store table"""

    # Get inspector to check current state
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Check if table exists
    tables = inspector.get_table_names()
    if 'gemini_file_search_store' not in tables:
        # Table doesn't exist, skip
        return

    # Check if column already exists
    columns = [col['name'] for col in inspector.get_columns('gemini_file_search_store')]
    if 'api_key_hash' in columns:
        # Column already exists, skip
        return

    # Add api_key_hash column (initially nullable)
    op.add_column('gemini_file_search_store',
                  sa.Column('api_key_hash', sa.String(length=64), nullable=True))

    # Update existing records with a placeholder hash
    # This assumes existing stores were created with the server's default API key
    # Users will need to provide their API key to create new stores or use existing ones
    op.execute("""
        UPDATE gemini_file_search_store
        SET api_key_hash = 'legacy_default_key_hash_placeholder'
        WHERE api_key_hash IS NULL
    """)

    # Make column non-nullable after populating existing records
    op.alter_column('gemini_file_search_store', 'api_key_hash',
                   existing_type=sa.String(length=64),
                   nullable=False)


def downgrade():
    """Remove api_key_hash column from gemini_file_search_store table"""

    # Get inspector to check current state
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Check if table exists
    tables = inspector.get_table_names()
    if 'gemini_file_search_store' not in tables:
        # Table doesn't exist, skip
        return

    # Check if column exists
    columns = [col['name'] for col in inspector.get_columns('gemini_file_search_store')]
    if 'api_key_hash' not in columns:
        # Column doesn't exist, skip
        return

    # Drop the column
    op.drop_column('gemini_file_search_store', 'api_key_hash')
