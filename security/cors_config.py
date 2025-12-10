"""CORS and Security Configuration Module.

Handles Cross-Origin Resource Sharing (CORS) configuration,
security headers, and protection against common web vulnerabilities.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CORSConfig:
    """CORS configuration manager."""

    # Production allowed origins
    ALLOWED_ORIGINS = [
        'https://api.faberlic-satire-rag.com',
        'https://app.faberlic-satire-rag.com',
        'https://dashboard.faberlic-satire-rag.com',
    ]

    # Development allowed origins
    DEV_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:8000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:8000',
    ]

    # Allowed HTTP methods
    ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']

    # Allowed request headers
    ALLOWED_HEADERS = [
        'Content-Type',
        'Authorization',
        'X-API-Key',
        'X-Request-ID',
        'Accept',
        'Accept-Encoding',
    ]

    # Headers exposed to client
    EXPOSED_HEADERS = [
        'X-RateLimit-Limit',
        'X-RateLimit-Remaining',
        'X-RateLimit-Reset',
        'X-Request-ID',
    ]

    # CORS configuration
    MAX_AGE = 3600  # 1 hour
    ALLOW_CREDENTIALS = True

    @classmethod
    def get_cors_headers(cls, origin: str, is_dev: bool = False) -> Dict[str, str]:
        """Get CORS headers for response.

        Args:
            origin: Request origin
            is_dev: Whether in development mode

        Returns:
            CORS headers dict
        """
        allowed = cls.DEV_ORIGINS if is_dev else cls.ALLOWED_ORIGINS

        if origin in allowed:
            return {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': ', '.join(cls.ALLOWED_METHODS),
                'Access-Control-Allow-Headers': ', '.join(cls.ALLOWED_HEADERS),
                'Access-Control-Expose-Headers': ', '.join(cls.EXPOSED_HEADERS),
                'Access-Control-Max-Age': str(cls.MAX_AGE),
                'Access-Control-Allow-Credentials': str(cls.ALLOW_CREDENTIALS),
            }
        return {}


class SecurityHeaders:
    """Security headers configuration."""

    # HSTS configuration
    HSTS_MAX_AGE = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = True

    # CSP configuration
    CSP_POLICY = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers.

        Returns:
            Security headers dict
        """
        return {
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            # Enable XSS protection
            'X-XSS-Protection': '1; mode=block',
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            # Permissions policy
            'Permissions-Policy': (
                'geolocation=(), '
                'microphone=(), '
                'camera=(), '
                'payment=()'
            ),
            # HSTS
            'Strict-Transport-Security': (
                f'max-age={SecurityHeaders.HSTS_MAX_AGE}; '
                f'includeSubDomains; '
                f'preload'
            ),
            # CSP
            'Content-Security-Policy': SecurityHeaders.CSP_POLICY,
            # Additional security
            'X-Permitted-Cross-Domain-Policies': 'none',
        }


class InputSanitizer:
    """Input sanitization utilities."""

    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        '<script',
        'javascript:',
        'on',  # Event handlers
        'eval(',
        'exec(',
    ]

    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitize user input.

        Args:
            user_input: Raw user input

        Returns:
            Sanitized input
        """
        if not isinstance(user_input, str):
            return str(user_input)

        sanitized = user_input.strip()

        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')

        # Check for dangerous patterns
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if pattern.lower() in sanitized.lower():
                logger.warning(
                    f'Dangerous pattern detected: {pattern}',
                    extra={'input_length': len(user_input)}
                )
                raise ValueError('Invalid input detected')

        return sanitized

    @staticmethod
    def sanitize_dict(data: Dict) -> Dict:
        """Sanitize dictionary values.

        Args:
            data: Dictionary with string values

        Returns:
            Dictionary with sanitized values
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_input(value)
            else:
                sanitized[key] = value
        return sanitized


class RateLimitConfig:
    """Rate limiting security configuration."""

    # IP-based rate limits
    IP_RATE_LIMITS = {
        'default': 100,  # requests per minute
        'login': 5,
        'password_reset': 3,
    }

    # User-based rate limits
    USER_RATE_LIMITS = {
        'free': 30,
        'premium': 300,
        'enterprise': 10000,
    }

    # Blacklist configuration
    BLACKLIST_ENABLED = True
    BLACKLIST_TTL = 3600  # 1 hour


class SecurityConfig:
    """Unified security configuration."""

    def __init__(self, is_production: bool = True):
        self.is_production = is_production
        self.cors = CORSConfig()
        self.headers = SecurityHeaders()
        self.sanitizer = InputSanitizer()
        self.rate_limit = RateLimitConfig()

    def get_all_security_headers(self, origin: str) -> Dict[str, str]:
        """Get all security headers.

        Args:
            origin: Request origin

        Returns:
            All security headers
        """
        headers = self.headers.get_security_headers()
        cors_headers = self.cors.get_cors_headers(
            origin, is_dev=not self.is_production
        )
        headers.update(cors_headers)
        return headers
