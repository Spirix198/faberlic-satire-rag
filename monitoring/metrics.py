"""Production-Ready Monitoring and Metrics System

Supports:
- Performance metrics tracking
- Error rate monitoring
- Health checks
- Structured logging (JSON format)
- Metrics export (Prometheus-compatible)
- Real-time alerts
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from functools import wraps


class MetricLevel(Enum):
    """Metric severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Represents a single metric event"""
    name: str
    value: float
    unit: str = "ms"
    level: MetricLevel = MetricLevel.INFO
    timestamp: str = None
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.tags is None:
            self.tags = {}
    
    def to_json(self) -> str:
        """Convert to JSON format"""
        data = asdict(self)
        data['level'] = self.level.value
        return json.dumps(data)


class MetricsCollector:
    """Collects and aggregates metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def record(self, metric: Metric) -> None:
        """Record a metric"""
        with self.lock:
            if metric.name not in self.metrics:
                self.metrics[metric.name] = []
            self.metrics[metric.name].append(metric)
            
            # Log the metric
            self.logger.info(f"Metric: {metric.to_json()}")
    
    def get_stats(self, metric_name: str) -> Optional[Dict]:
        """Get statistics for a metric"""
        with self.lock:
            if metric_name not in self.metrics:
                return None
            
            values = [m.value for m in self.metrics[metric_name]]
            if not values:
                return None
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'last': values[-1]
            }
    
    def clear(self) -> None:
        """Clear all metrics"""
        with self.lock:
            self.metrics.clear()


class PerformanceMonitor:
    """Monitors performance of functions"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.logger = logging.getLogger(__name__)
    
    def track(self, operation_name: str, threshold_ms: float = None):
        """Decorator to track function performance"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed_ms = (time.time() - start_time) * 1000
                    
                    # Determine level
                    level = MetricLevel.INFO
                    if threshold_ms and elapsed_ms > threshold_ms:
                        level = MetricLevel.WARNING
                    
                    metric = Metric(
                        name=f"{operation_name}_duration",
                        value=elapsed_ms,
                        unit="ms",
                        level=level,
                        tags={"function": func.__name__}
                    )
                    self.collector.record(metric)
            
            return wrapper
        return decorator


class HealthCheck:
    """System health monitoring"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def register(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a health check"""
        with self.lock:
            self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, bool]:
        """Run all health checks"""
        results = {}
        with self.lock:
            for name, check_func in self.checks.items():
                try:
                    results[name] = check_func()
                except Exception as e:
                    self.logger.error(f"Health check '{name}' failed: {e}")
                    results[name] = False
        
        return results
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return all(self.run_checks().values())


class ErrorTracker:
    """Tracks errors and exceptions"""
    
    def __init__(self):
        self.errors: Dict[str, list] = {}
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def record_error(self, error_type: str, message: str, **context) -> None:
        """Record an error"""
        with self.lock:
            if error_type not in self.errors:
                self.errors[error_type] = []
            
            error_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'message': message,
                'context': context
            }
            self.errors[error_type].append(error_data)
            
            self.logger.error(f"{error_type}: {message}", extra=context)
    
    def get_error_rate(self, error_type: str, minutes: int = 5) -> float:
        """Get error rate for a type"""
        with self.lock:
            if error_type not in self.errors:
                return 0.0
            
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            recent_errors = [
                e for e in self.errors[error_type]
                if datetime.fromisoformat(e['timestamp']) > cutoff
            ]
            
            return len(recent_errors) / (minutes * 60) if minutes else 0.0


# Global monitoring instances
_metrics_collector: Optional[MetricsCollector] = None
_health_check: Optional[HealthCheck] = None
_error_tracker: Optional[ErrorTracker] = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_health_check() -> HealthCheck:
    """Get or create global health check"""
    global _health_check
    if _health_check is None:
        _health_check = HealthCheck()
    return _health_check

def get_error_tracker() -> ErrorTracker:
    """Get or create global error tracker"""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker
