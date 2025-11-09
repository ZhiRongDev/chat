"""Migrate to Gemini File Search

Revision ID: 001_gemini_file_search
Revises:
Create Date: 2025-01-09

This migration:
1. Adds Gemini File Search fields to the document table
2. Creates new gemini_file_search_store table
3. Drops old document_chunk and vector_store_config tables

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_gemini_file_search'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Apply migration to upgrade to Gemini File Search"""

    # Create gemini_file_search_store table
    op.create_table(
        'gemini_file_search_store',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('store_name', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('document_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_size_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Add new columns to document table
    op.add_column('document', sa.Column('gemini_file_id', sa.String(length=255), nullable=True))
    op.add_column('document', sa.Column('gemini_store_id', sa.String(length=255), nullable=True))
    op.add_column('document', sa.Column('gemini_mime_type', sa.String(length=100), nullable=True))
    op.add_column('document', sa.Column('gemini_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Remove old column from document table
    op.drop_column('document', 'chunk_count')

    # Drop old tables (in correct order due to foreign keys)
    op.drop_table('document_chunk')
    op.drop_table('vector_store_config')


def downgrade():
    """Rollback migration to restore old RAG system"""

    # Recreate vector_store_config table
    op.create_table(
        'vector_store_config',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('store_type', sa.String(length=50), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('embedding_dimension', sa.Integer(), nullable=False),
        sa.Column('distance_metric', sa.String(length=20), nullable=False, server_default='cosine'),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('document_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Recreate document_chunk table
    op.create_table(
        'document_chunk',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('document_id', sa.BigInteger(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('vector_id', sa.String(length=255), nullable=False),
        sa.Column('extra_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['document.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Add back chunk_count column to document table
    op.add_column('document', sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'))

    # Remove Gemini columns from document table
    op.drop_column('document', 'gemini_metadata')
    op.drop_column('document', 'gemini_mime_type')
    op.drop_column('document', 'gemini_store_id')
    op.drop_column('document', 'gemini_file_id')

    # Drop gemini_file_search_store table
    op.drop_table('gemini_file_search_store')
