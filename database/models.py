"""SQLAlchemy ORM models for Faberlic Satire RAG system.

Defines database tables for content, users, analytics, and system metadata.
"""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Float, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from database.db_config import Base


class User(Base):
    """User model for authentication and tracking."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    contents = relationship("Content", back_populates="author", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class APIKey(Base):
    """API Key model for user authentication."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    rate_limit = Column(Integer, default=1000, doc="Requests per minute")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, user_id={self.user_id}, name={self.name})>"


class Content(Base):
    """Generated content model."""

    __tablename__ = "content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    body = Column(Text, nullable=False)
    style = Column(String(50), nullable=False, index=True, comment="e.g., satirical, witty, sharp")
    language = Column(String(10), default="ru", index=True)
    status = Column(String(20), default="draft", index=True, comment="draft, published, archived")
    
    # Generation metadata
    prompt = Column(Text, nullable=True)
    model_used = Column(String(100), nullable=False, comment="e.g., pplx-70b-online")
    tokens_used = Column(Integer, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    
    # Content metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # URLs and social media
    medium_url = Column(String(500), nullable=True, unique=True, index=True)
    telegram_post_id = Column(String(100), nullable=True, unique=True)
    twitter_url = Column(String(500), nullable=True, unique=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Additional metadata
    metadata_json = Column(JSONB, nullable=True, comment="Additional JSON metadata")
    tags = Column(String(500), nullable=True, comment="Comma-separated tags")

    # Relationships
    author = relationship("User", back_populates="contents")
    analytics = relationship("Analytics", back_populates="content", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_content_user_created", "user_id", "created_at"),
        Index("ix_content_status_published", "status", "published_at"),
        CheckConstraint("status IN ('draft', 'published', 'archived')"),
    )

    def __repr__(self) -> str:
        return f"<Content(id={self.id}, title={self.title[:50]}, status={self.status})>"


class Analytics(Base):
    """Analytics and usage tracking."""

    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=True, index=True)
    
    event_type = Column(String(50), nullable=False, index=True, comment="e.g., view, generate, publish, error")
    event_category = Column(String(50), nullable=False, index=True, comment="e.g., content, api, system")
    
    # Request/Response details
    endpoint = Column(String(255), nullable=True, comment="API endpoint called")
    method = Column(String(20), nullable=True, comment="HTTP method")
    status_code = Column(Integer, nullable=True, index=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Request metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 and IPv6
    request_id = Column(String(100), unique=True, nullable=True, index=True)
    
    # Additional context
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="analytics")
    content = relationship("Content", back_populates="analytics")

    __table_args__ = (
        Index("ix_analytics_user_created", "user_id", "created_at"),
        Index("ix_analytics_event_created", "event_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Analytics(id={self.id}, event_type={self.event_type}, created_at={self.created_at})>"


class SystemMetadata(Base):
    """System-wide metadata and configuration."""

    __tablename__ = "system_metadata"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), default="string", comment="string, integer, boolean, json")
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<SystemMetadata(key={self.key}, value={self.value[:50]})>"


class RAGVector(Base):
    """Store RAG vectors for semantic search."""

    __tablename__ = "rag_vectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=True, index=True)
    
    # Vector data (for embedding storage)
    vector_text = Column(Text, nullable=False, comment="Original text for embedding")
    embedding_model = Column(String(100), nullable=False, comment="e.g., sentence-transformers/multilingual-MiniLM")
    
    # Vector metadata
    chunk_index = Column(Integer, nullable=False, comment="Position in original document")
    vector_dimension = Column(Integer, nullable=False, comment="Embedding dimension")
    
    # Storage and timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_rag_vectors_content_chunk", "content_id", "chunk_index"),
    )

    def __repr__(self) -> str:
        return f"<RAGVector(id={self.id}, content_id={self.content_id}, chunk_index={self.chunk_index})>"
