"""JWT authentication utilities for Faberlic Satire RAG.

Provides JWT token generation, validation, and refresh mechanisms.
Includes password hashing and user verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID
import logging
import os
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    user_id: UUID
    email: str
    username: str
    is_admin: bool = False
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    token_type: str = "access"  # access or refresh


class TokenResponse(BaseModel):
    """Token response structure."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds


class PasswordUtils:
    """Utilities for password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database

        Returns:
            True if passwords match, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)


class JWTUtils:
    """Utilities for JWT token generation and validation."""

    @staticmethod
    def create_access_token(
        user_id: UUID,
        email: str,
        username: str,
        is_admin: bool = False,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT access token.

        Args:
            user_id: User ID
            email: User email
            username: Username
            is_admin: Whether user is admin
            expires_delta: Custom expiration time

        Returns:
            Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        payload = {
            "user_id": str(user_id),
            "email": email,
            "username": username,
            "is_admin": is_admin,
            "token_type": "access",
            "iat": now,
            "exp": expire,
        }

        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Access token created for user: {username}")
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        user_id: UUID,
        email: str,
        username: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT refresh token.

        Args:
            user_id: User ID
            email: User email
            username: Username
            expires_delta: Custom expiration time

        Returns:
            Encoded JWT refresh token
        """
        if expires_delta is None:
            expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        payload = {
            "user_id": str(user_id),
            "email": email,
            "username": username,
            "token_type": "refresh",
            "iat": now,
            "exp": expire,
        }

        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Refresh token created for user: {username}")
        return encoded_jwt

    @staticmethod
    def create_token_pair(
        user_id: UUID,
        email: str,
        username: str,
        is_admin: bool = False,
    ) -> Dict[str, str]:
        """Create both access and refresh tokens.

        Args:
            user_id: User ID
            email: User email
            username: Username
            is_admin: Whether user is admin

        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = JWTUtils.create_access_token(
            user_id=user_id,
            email=email,
            username=username,
            is_admin=is_admin,
        )
        refresh_token = JWTUtils.create_refresh_token(
            user_id=user_id,
            email=email,
            username=username,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[TokenPayload]:
        """Verify and decode JWT token.

        Args:
            token: JWT token string
            token_type: Expected token type (access or refresh)

        Returns:
            TokenPayload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Verify token type
            if payload.get("token_type") != token_type:
                logger.warning(f"Token type mismatch: expected {token_type}")
                return None

            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            return None

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token if refresh token is valid, None otherwise
        """
        payload = JWTUtils.verify_token(refresh_token, token_type="refresh")

        if not payload:
            logger.warning("Invalid or expired refresh token")
            return None

        new_access_token = JWTUtils.create_access_token(
            user_id=UUID(payload.user_id),
            email=payload.email,
            username=payload.username,
            is_admin=payload.is_admin,
        )
        logger.info(f"Access token refreshed for user: {payload.username}")
        return new_access_token
