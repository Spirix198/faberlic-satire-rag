"""Event Tracking and Analytics Module

This module provides event tracking and analytics functionality for the Faberlic RAG system.
It tracks user interactions, content generation events, and system performance metrics.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class EventTracker:
    """Tracks application events for analytics and monitoring."""

    def __init__(self, metrics_service=None):
        """Initialize the event tracker.
        
        Args:
            metrics_service: Optional service for sending metrics
        """
        self.metrics_service = metrics_service
        self.event_buffer = []

    def track_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Track an event.
        
        Args:
            event_type: Type of event to track
            data: Event data dictionary
        """
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'data': data
        }
        self.event_buffer.append(event)
        logger.info(f"Event tracked: {event_type}")
        
        if self.metrics_service:
            self.metrics_service.record_event(event_type)

    def track_content_generation(self, prompt: str, generated_text: str, 
                                latency_ms: float) -> None:
        """Track content generation event.
        
        Args:
            prompt: The input prompt
            generated_text: Generated content
            latency_ms: Generation latency in milliseconds
        """
        self.track_event('content_generation', {
            'prompt_length': len(prompt),
            'text_length': len(generated_text),
            'latency_ms': latency_ms
        })

    def track_api_request(self, endpoint: str, method: str, 
                         status_code: int, response_time_ms: float) -> None:
        """Track API request event.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
        """
        self.track_event('api_request', {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time_ms
        })

    def get_events(self) -> list:
        """Get all tracked events."""
        return self.event_buffer.copy()

    def clear_events(self) -> None:
        """Clear event buffer."""
        self.event_buffer.clear()
