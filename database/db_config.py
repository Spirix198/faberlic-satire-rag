"""Database configuration and connection pooling.

This module manages PostgreSQL connections with SQLAlchemy ORM,
including connection pooling, session management, and health checks.

Security: All database credentials are loaded from environment variables.
"""

import os
from typing import Generator, Optional
from contextlib import contextmanager
import logging

from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DBAPIError

logger = logging.getLogger(__name__)

# SQLAlchemy ORM Base
Base = declarative_base()


class DatabaseConfig:
    """Database configuration with connection pooling."""

    def __init__(
        self,
        db_url: Optional[str] = None,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
    ):
        """
        Initialize database configuration.

        Args:
            db_url: Database URL (defaults to DATABASE_URL env var)
            pool_size: Number of connections to maintain in pool
            max_overflow: Maximum overflow connections
            pool_timeout: Timeout for getting connection from pool (seconds)
            pool_recycle: Recycle connections after N seconds (prevents timeout)
            echo: Enable SQL query logging
        """
        self.db_url = db_url or os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/faberlic_satire",
        )
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo

        # Validate DATABASE_URL format
        if not self._validate_db_url():
            logger.warning(
                f"Database URL may be invalid. Using: {self.db_url[:20]}..."
            )

    def _validate_db_url(self) -> bool:
        """Validate database URL format."""
        return self.db_url.startswith(("postgresql://", "postgresql+psycopg2://"))

    def get_engine(self):
        """Create SQLAlchemy engine with connection pooling."""
        engine = create_engine(
            self.db_url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            echo=self.echo,
            # Connection pooling options
            connect_args={
                "timeout": 30,
                "check_same_thread": False,
            },
        )

        # Add event listeners for connection management
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Execute pragmas on new connections."""
            cursor = dbapi_conn.cursor()
            cursor.execute("SET timezone = 'UTC'")
            cursor.close()

        @event.listens_for(engine, "pool_connect")
        def receive_pool_connect(dbapi_conn, connection_record):
            """Log pool connection events."""
            logger.debug("New connection from pool established")

        logger.info(f"Database engine created with pool_size={self.pool_size}")
        return engine

    async def health_check(self, engine) -> bool:
        """Check database connection health."""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except DBAPIError as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during health check: {str(e)}")
            return False


class SessionManager:
    """Manages SQLAlchemy session lifecycle."""

    def __init__(self, engine):
        """Initialize session manager.

        Args:
            engine: SQLAlchemy engine instance
        """
        self.engine = engine
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for database session.

        Usage:
            with session_manager.session_scope() as session:
                session.add(obj)
                session.commit()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database transaction failed: {str(e)}")
            raise
        finally:
            session.close()

    def close(self):
        """Close all connections in the pool."""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global instances (lazy initialized)
_db_config: Optional[DatabaseConfig] = None
_session_manager: Optional[SessionManager] = None


def get_db_config() -> DatabaseConfig:
    """Get or create database configuration."""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
    return _db_config


def get_session_manager() -> SessionManager:
    """Get or create session manager."""
    global _session_manager
    if _session_manager is None:
        config = get_db_config()
        engine = config.get_engine()
        _session_manager = SessionManager(engine)
    return _session_manager


def get_session() -> Session:
    """Get a new database session (FastAPI dependency).

    Usage in FastAPI:
        @app.get("/items/")
        def read_items(session: Session = Depends(get_session)):
            return session.query(Item).all()
    """
    return get_session_manager().get_session()


def create_all_tables():
    """Create all database tables."""
    config = get_db_config()
    engine = config.get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("All database tables created")


def drop_all_tables():
    """Drop all database tables (use with caution!)."""
    config = get_db_config()
    engine = config.get_engine()
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")
