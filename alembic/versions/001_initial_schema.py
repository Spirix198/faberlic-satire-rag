"""Initial database schema migration.

Revision ID: 001
Revises:
Create Date: 2025-12-10

This is the initial migration that creates all tables for the Faberlic Satire RAG system:
- user_account table (User model)
- api_key table (APIKey model)
- content table (Content model)
- analytics table (Analytics model)
- system_metadata table (SystemMetadata model)
- rag_vector table (RAGVector model)
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade function: Create all initial tables."""
    # Create user_account table
    op.create_table(
        'user_account',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Create api_key table
    op.create_table(
        'api_key',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_account.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )

    # Create content table
    op.create_table(
        'content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_account.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create analytics table
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Float(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_account.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create system_metadata table
    op.create_table(
        'system_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # Create rag_vector table
    op.create_table(
        'rag_vector',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('vector_data', sa.Text(), nullable=False),
        sa.Column('embedding_model', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better query performance
    op.create_index('ix_api_key_user_id', 'api_key', ['user_id'])
    op.create_index('ix_content_user_id', 'content', ['user_id'])
    op.create_index('ix_analytics_user_id', 'analytics', ['user_id'])
    op.create_index('ix_analytics_timestamp', 'analytics', ['timestamp'])
    op.create_index('ix_rag_vector_content_id', 'rag_vector', ['content_id'])


def downgrade() -> None:
    """Downgrade function: Drop all tables."""
    # Drop indexes
    op.drop_index('ix_rag_vector_content_id')
    op.drop_index('ix_analytics_timestamp')
    op.drop_index('ix_analytics_user_id')
    op.drop_index('ix_content_user_id')
    op.drop_index('ix_api_key_user_id')
    
    # Drop tables in reverse order of dependencies
    op.drop_table('rag_vector')
    op.drop_table('system_metadata')
    op.drop_table('analytics')
    op.drop_table('content')
    op.drop_table('api_key')
    op.drop_table('user_account')
