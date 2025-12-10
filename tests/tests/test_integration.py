"""API tests for Faberlic Satire RAG system.

Comprehensive unit tests for API endpoints, rate limiting,
error handling, and core functionality.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check_success(self):
        """Health check returns 200 with status."""
        from api import app
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert 'version' in data

    def test_health_includes_timestamp(self):
        """Health response includes timestamp."""
        from api import app
        with app.test_client() as client:
            response = client.get('/health')
            data = json.loads(response.data)
            assert 'timestamp' in data
            # Verify timestamp is ISO format
            datetime.fromisoformat(data['timestamp'])


class TestGenerateEndpoint:
    """Tests for /api/generate endpoint."""

    def test_generate_requires_authentication(self):
        """Generate endpoint requires API key."""
        from api import app
        with app.test_client() as client:
            response = client.post('/api/generate',
                                 json={'prompt': 'test'})
            assert response.status_code == 401

    def test_generate_validates_input(self):
        """Generate validates required parameters."""
        from api import app
        with app.test_client() as client:
            response = client.post(
                '/api/generate',
                headers={'Authorization': 'Bearer test_key'},
                json={}
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

    @patch('api.generate_content')
    def test_generate_returns_content(self, mock_generate):
        """Generate returns generated content."""
        mock_generate.return_value = 'Generated satirical text'
        from api import app
        with app.test_client() as client:
            response = client.post(
                '/api/generate',
                headers={'Authorization': 'Bearer test_key'},
                json={'prompt': 'Technology humor'}
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'content' in data


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def test_rate_limiter_allows_requests_below_limit(self):
        """Rate limiter allows requests below limit."""
        from rate_limiting import TokenBucketRateLimiter
        limiter = TokenBucketRateLimiter(rate=100, capacity=100)
        for _ in range(50):
            assert limiter.allow_request() is True

    def test_rate_limiter_blocks_above_limit(self):
        """Rate limiter blocks requests above limit."""
        from rate_limiting import TokenBucketRateLimiter
        limiter = TokenBucketRateLimiter(rate=2, capacity=2)
        # Exhaust tokens
        limiter.allow_request()
        limiter.allow_request()
        # This should fail
        assert limiter.allow_request() is False

    def test_per_client_rate_limiting(self):
        """Per-client rate limiting works correctly."""
        from rate_limiting import PerClientRateLimiter
        limiter = PerClientRateLimiter(rate=5, capacity=5)
        # Different clients get separate limits
        assert limiter.allow_request('client1') is True
        assert limiter.allow_request('client2') is True


class TestExceptionHandling:
    """Tests for exception handling."""

    def test_validation_error_response(self):
        """ValidationError returns 400."""
        from errors import ValidationError
        exc = ValidationError('Invalid input')
        assert exc.status_code == 400
        assert exc.error_code == 'VALIDATION_ERROR'

    def test_authentication_error_response(self):
        """AuthenticationError returns 401."""
        from errors import AuthenticationError
        exc = AuthenticationError()
        assert exc.status_code == 401
        assert exc.error_code == 'AUTHENTICATION_ERROR'

    def test_rate_limit_error_response(self):
        """RateLimitError returns 429."""
        from errors import RateLimitError
        exc = RateLimitError(remaining_seconds=60)
        assert exc.status_code == 429
        assert exc.error_code == 'RATE_LIMIT_EXCEEDED'
        assert exc.retry_after == 60

    def test_exception_to_dict(self):
        """Exceptions convert to dict format."""
        from errors import APIException
        exc = APIException('Test error', 400, 'TEST_ERROR')
        exc_dict = exc.to_dict()
        assert 'error' in exc_dict
        assert exc_dict['error']['code'] == 'TEST_ERROR'
        assert exc_dict['error']['status_code'] == 400


class TestCaching:
    """Tests for caching functionality."""

    def test_lru_cache_stores_items(self):
        """LRU cache stores and retrieves items."""
        from caching import LRUCache
        cache = LRUCache(max_size=3)
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

    def test_lru_cache_evicts_old_items(self):
        """LRU cache evicts oldest items."""
        from caching import LRUCache
        cache = LRUCache(max_size=2)
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')  # Should evict key1
        assert cache.get('key1') is None
        assert cache.get('key2') == 'value2'


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""

    @patch('api.generate_content')
    def test_full_request_cycle(self, mock_generate):
        """Full request cycle works correctly."""
        mock_generate.return_value = 'Generated content'
        from api import app
        with app.test_client() as client:
            # Make authenticated request
            response = client.post(
                '/api/generate',
                headers={'Authorization': 'Bearer valid_key'},
                json={'prompt': 'test', 'style': 'zadornov'}
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'id' in data
            assert 'content' in data
            assert 'generated_at' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
