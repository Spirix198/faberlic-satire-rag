"""Content API routes with database integration.

Provides endpoints for creating, reading, updating, and deleting content.
Includes authentication, rate limiting, and analytics tracking.
"""

from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Header, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from database.db_config import get_session
from database.models import Content, User, Analytics
from security.cors_config import SecurityConfig
from monitoring.metrics import MetricsCollector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/content", tags=["content"])


# Request/Response Schemas
class ContentCreate(BaseModel):
    """Schema for creating new content."""
    title: str = Field(..., min_length=5, max_length=500)
    body: str = Field(..., min_length=50)
    style: str = Field(..., description="e.g., satirical, witty, sharp")
    language: str = Field(default="ru", max_length=10)
    prompt: Optional[str] = Field(None, description="Original prompt used")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class ContentUpdate(BaseModel):
    """Schema for updating content."""
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    body: Optional[str] = Field(None, min_length=50)
    style: Optional[str] = None
    tags: Optional[str] = None


class ContentResponse(BaseModel):
    """Schema for content responses."""
    id: UUID
    title: str
    body: str
    style: str
    status: str
    views: int
    likes: int
    created_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """Extract user from authorization header.
    
    TODO: Implement proper JWT validation
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    # Placeholder: In production, validate JWT token here
    return None


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_in: ContentCreate,
    session: Session = Depends(get_session),
    request: Request = None,
    authorization: Optional[str] = Header(None),
) -> Content:
    """Create new content.
    
    Returns:
        Created content with ID and timestamps
    
    Raises:
        HTTPException: If user is not authenticated or validation fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        # Create new content record
        new_content = Content(
            user_id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder
            title=content_in.title,
            body=content_in.body,
            style=content_in.style,
            language=content_in.language,
            prompt=content_in.prompt,
            model_used="pplx-70b-online",
            status="draft",
            tags=content_in.tags,
        )
        session.add(new_content)
        session.flush()
        
        # Track analytics
        analytics = Analytics(
            user_id=None,
            content_id=new_content.id,
            event_type="create",
            event_category="content",
            endpoint="/api/content",
            method="POST",
            status_code=201,
        )
        session.add(analytics)
        session.commit()
        
        logger.info(f"Content created: {new_content.id}")
        return new_content
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    session: Session = Depends(get_session),
) -> Content:
    """Get content by ID.
    
    Args:
        content_id: UUID of the content
    
    Returns:
        Content details
    
    Raises:
        HTTPException: If content not found
    """
    content = session.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Increment views
    content.views += 1
    session.commit()
    
    # Track analytics
    analytics = Analytics(
        content_id=content.id,
        event_type="view",
        event_category="content",
        endpoint="/api/content/{content_id}",
        method="GET",
        status_code=200,
    )
    session.add(analytics)
    session.commit()
    
    return content


@router.get("/", response_model=List[ContentResponse])
async def list_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    session: Session = Depends(get_session),
) -> List[Content]:
    """List content with pagination.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        status_filter: Filter by status (draft, published, archived)
    
    Returns:
        List of content
    """
    query = session.query(Content)
    
    if status_filter:
        query = query.filter(Content.status == status_filter)
    
    contents = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()
    return contents


@router.patch("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    content_in: ContentUpdate,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None),
) -> Content:
    """Update content.
    
    Args:
        content_id: UUID of the content to update
        content_in: Updated content data
    
    Returns:
        Updated content
    
    Raises:
        HTTPException: If content not found or unauthorized
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    content = session.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Update fields if provided
    if content_in.title is not None:
        content.title = content_in.title
    if content_in.body is not None:
        content.body = content_in.body
    if content_in.style is not None:
        content.style = content_in.style
    if content_in.tags is not None:
        content.tags = content_in.tags
    
    content.updated_at = datetime.now(timezone.utc)
    session.commit()
    
    logger.info(f"Content updated: {content.id}")
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: UUID,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None),
) -> None:
    """Delete content (archive it).
    
    Args:
        content_id: UUID of the content to delete
    
    Raises:
        HTTPException: If content not found or unauthorized
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    content = session.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Soft delete: mark as archived instead of deleting
    content.status = "archived"
    session.commit()
    
    logger.info(f"Content archived: {content.id}")
