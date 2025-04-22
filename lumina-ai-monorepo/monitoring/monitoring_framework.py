"""
Monitoring Framework for Lumina AI

This module provides a comprehensive monitoring framework for the Lumina AI platform,
including metrics collection, distributed tracing, log aggregation, health checks,
alerting, and visualization capabilities.
"""

import logging
import time
import os
import json
from typing import Dict, List, Any, Optional, Union
import threading
import socket
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects and manages metrics from various components of the Lumina AI system.
    Supports counters, gauges, histograms, and summaries.
    """
    
    def __init__(self, service_name: str, instance_id: Optional[str] = None):
        """
        Initialize the metrics collector.
        
        Args:
            service_name: Name of the service being monitored
            instance_id: Optional unique identifier for this service instance
        """
        self.service_name = service_name
        self.instance_id = instance_id or socket.gethostname()
        self.metrics = {
            "counters": {},
            "gauges": {},
            "histograms": {},
            "summaries": {}
        }
        self.dimensions = {
            "service": service_name,
            "instance": self.instance_id,
            "environment": os.environ.get("ENVIRONMENT", "development")
        }
        self._lock = threading.Lock()
        logger.info(f"Initialized MetricsCollector for service {service_name}, instance {self.instance_id}")
    
    def increment_counter(self, name: str, value: int = 1, dimensions: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Name of the counter
            value: Value to increment by (default: 1)
            dimensions: Additional dimensions for this metric
        """
        with self._lock:
            if name not in self.metrics["counters"]:
                self.metrics["counters"][name] = 0
            self.metrics["counters"][name] += value
            
            # Log the metric
            metric_dimensions = {**self.dimensions, **(dimensions or {})}
            logger.debug(f"Counter {name} incremented by {value}: {self.metrics['counters'][name]}, dimensions: {metric_dimensions}")
    
    def set_gauge(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric to a specific value.
        
        Args:
            name: Name of the gauge
            value: Value to set
            dimensions: Additional dimensions for this metric
        """
        with self._lock:
            self.metrics["gauges"][name] = value
            
            # Log the metric
            metric_dimensions = {**self.dimensions, **(dimensions or {})}
            logger.debug(f"Gauge {name} set to {value}, dimensions: {metric_dimensions}")
    
    def record_histogram(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> None:
        """
        Record a value in a histogram metric.
        
        Args:
            name: Name of the histogram
            value: Value to record
            dimensions: Additional dimensions for this metric
        """
        with self._lock:
            if name not in self.metrics["histograms"]:
                self.metrics["histograms"][name] = []
            self.metrics["histograms"][name].append(value)
            
            # Log the metric
            metric_dimensions = {**self.dimensions, **(dimensions or {})}
            logger.debug(f"Histogram {name} recorded value {value}, dimensions: {metric_dimensions}")
    
    def record_summary(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> None:
        """
        Record a value in a summary metric.
        
        Args:
            name: Name of the summary
            value: Value to record
            dimensions: Additional dimensions for this metric
        """
        with self._lock:
            if name not in self.metrics["summaries"]:
                self.metrics["summaries"][name] = []
            self.metrics["summaries"][name].append(value)
            
            # Log the metric
            metric_dimensions = {**self.dimensions, **(dimensions or {})}
            logger.debug(f"Summary {name} recorded value {value}, dimensions: {metric_dimensions}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary containing all metrics
        """
        with self._lock:
            # Process histograms and summaries to calculate statistics
            processed_metrics = {
                "counters": self.metrics["counters"].copy(),
                "gauges": self.metrics["gauges"].copy(),
                "histograms": {},
                "summaries": {}
            }
            
            # Process histograms
            for name, values in self.metrics["histograms"].items():
                if values:
                    processed_metrics["histograms"][name] = {
                        "count": len(values),
                        "sum": sum(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values)
                    }
            
            # Process summaries
            for name, values in self.metrics["summaries"].items():
                if values:
                    sorted_values = sorted(values)
                    processed_metrics["summaries"][name] = {
                        "count": len(values),
                        "sum": sum(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "p50": sorted_values[len(sorted_values) // 2],
                        "p90": sorted_values[int(len(sorted_values) * 0.9)],
                        "p95": sorted_values[int(len(sorted_values) * 0.95)],
                        "p99": sorted_values[int(len(sorted_values) * 0.99)]
                    }
            
            return {
                "metrics": processed_metrics,
                "dimensions": self.dimensions,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def reset_metrics(self) -> None:
        """Reset all metrics to their initial state."""
        with self._lock:
            self.metrics = {
                "counters": {},
                "gauges": {},
                "histograms": {},
                "summaries": {}
            }
            logger.info(f"Metrics reset for service {self.service_name}, instance {self.instance_id}")


class DistributedTracer:
    """
    Provides distributed tracing capabilities for tracking requests across services.
    """
    
    def __init__(self, service_name: str, instance_id: Optional[str] = None):
        """
        Initialize the distributed tracer.
        
        Args:
            service_name: Name of the service being traced
            instance_id: Optional unique identifier for this service instance
        """
        self.service_name = service_name
        self.instance_id = instance_id or socket.gethostname()
        self.active_spans = {}
        self._lock = threading.Lock()
        self._span_id_counter = 0
        logger.info(f"Initialized DistributedTracer for service {service_name}, instance {self.instance_id}")
    
    def _generate_span_id(self) -> str:
        """Generate a unique span ID."""
        with self._lock:
            self._span_id_counter += 1
            return f"{self.instance_id}-{int(time.time())}-{self._span_id_counter}"
    
    def start_span(self, name: str, parent_span_id: Optional[str] = None, 
                  attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new tracing span.
        
        Args:
            name: Name of the span
            parent_span_id: Optional ID of the parent span
            attributes: Optional attributes to attach to the span
            
        Returns:
            Unique ID for the new span
        """
        span_id = self._generate_span_id()
        start_time = time.time()
        
        span = {
            "id": span_id,
            "name": name,
            "service": self.service_name,
            "instance": self.instance_id,
            "parent_id": parent_span_id,
            "start_time": start_time,
            "attributes": attributes or {},
            "events": [],
            "status": "ACTIVE"
        }
        
        with self._lock:
            self.active_spans[span_id] = span
        
        logger.debug(f"Started span {name} with ID {span_id}, parent: {parent_span_id}")
        return span_id
    
    def end_span(self, span_id: str, status: str = "OK", 
                attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        End a tracing span.
        
        Args:
            span_id: ID of the span to end
            status: Status of the span (OK, ERROR)
            attributes: Optional additional attributes to attach
            
        Returns:
            The completed span data
        """
        end_time = time.time()
        
        with self._lock:
            if span_id not in self.active_spans:
                logger.warning(f"Attempted to end non-existent span with ID {span_id}")
                return {}
            
            span = self.active_spans[span_id]
            span["end_time"] = end_time
            span["duration"] = end_time - span["start_time"]
            span["status"] = status
            
            if attributes:
                span["attributes"].update(attributes)
            
            # Remove from active spans
            del self.active_spans[span_id]
        
        logger.debug(f"Ended span {span['name']} with ID {span_id}, status: {status}, duration: {span['duration']:.6f}s")
        return span
    
    def add_event(self, span_id: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an event to a span.
        
        Args:
            span_id: ID of the span
            name: Name of the event
            attributes: Optional attributes for the event
        """
        event_time = time.time()
        event = {
            "name": name,
            "time": event_time,
            "attributes": attributes or {}
        }
        
        with self._lock:
            if span_id not in self.active_spans:
                logger.warning(f"Attempted to add event to non-existent span with ID {span_id}")
                return
            
            self.active_spans[span_id]["events"].append(event)
        
        logger.debug(f"Added event {name} to span {span_id}")
    
    def set_span_attribute(self, span_id: str, key: str, value: Any) -> None:
        """
        Set an attribute on a span.
        
        Args:
            span_id: ID of the span
            key: Attribute key
            value: Attribute value
        """
        with self._lock:
            if span_id not in self.active_spans:
                logger.warning(f"Attempted to set attribute on non-existent span with ID {span_id}")
                return
            
            self.active_spans[span_id]["attributes"][key] = value
        
        logger.debug(f"Set attribute {key}={value} on span {span_id}")
    
    def get_active_spans(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all currently active spans.
        
        Returns:
            Dictionary of active spans
        """
        with self._lock:
            return self.active_spans.copy()


class HealthChecker:
    """
    Provides health checking capabilities for monitoring system health.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize the health checker.
        
        Args:
            service_name: Name of the service being monitored
        """
        self.service_name = service_name
        self.health_checks = {}
        self._lock = threading.Lock()
        logger.info(f"Initialized HealthChecker for service {service_name}")
    
    def register_health_check(self, name: str, check_function, interval_seconds: int = 60) -> None:
        """
        Register a new health check.
        
        Args:
            name: Name of the health check
            check_function: Function that performs the health check and returns (status, details)
            interval_seconds: How often to run the check
        """
        with self._lock:
            self.health_checks[name] = {
                "function": check_function,
                "interval": interval_seconds,
                "last_run": 0,
                "status": "UNKNOWN",
                "details": None
            }
        
        logger.info(f"Registered health check {name} with interval {interval_seconds}s")
    
    def run_health_check(self, name: str) -> Dict[str, Any]:
        """
        Run a specific health check.
        
        Args:
            name: Name of the health check to run
            
        Returns:
            Health check result
        """
        with self._lock:
            if name not in self.health_checks:
                logger.warning(f"Attempted to run non-existent health check {name}")
                return {"status": "UNKNOWN", "details": "Health check not found"}
            
            check = self.health_checks[name]
        
        try:
            status, details = check["function"]()
            
            with self._lock:
                self.health_checks[name]["last_run"] = time.time()
                self.health_checks[name]["status"] = status
                self.health_checks[name]["details"] = details
            
            logger.debug(f"Health check {name} completed with status {status}")
            return {"status": status, "details": details}
        except Exception as e:
            logger.error(f"Health check {name} failed: {str(e)}")
            
            with self._lock:
                self.health_checks[name]["last_run"] = time.time()
                self.health_checks[name]["status"] = "ERROR"
                self.health_checks[name]["details"] = str(e)
            
            return {"status": "ERROR", "details": str(e)}
    
    def run_all_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """
        Run all registered health checks.
        
        Returns:
            Dictionary of health check results
        """
        results = {}
        
        with self._lock:
            check_names = list(self.health_checks.keys())
        
        for name in check_names:
            results[name] = self.run_health_check(name)
        
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the overall health status.
        
        Returns:
            Health status information
        """
        with self._lock:
            checks = {name: {
                "status": check["status"],
                "details": check["details"],
                "last_run": check["last_run"]
            } for name, check in self.health_checks.items()}
        
        # Determine overall status
        if not checks:
            overall_status = "UNKNOWN"
        elif any(check["status"] == "ERROR" for check in checks.values()):
            overall_status = "ERROR"
        elif any(check["status"] == "WARNING" for check in checks.values()):
            overall_status = "WARNING"
        elif all(check["status"] == "OK" for check in checks.values()):
            overall_status = "OK"
        else:
            overall_status = "DEGRADED"
        
        return {
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "status": overall_status,
            "checks": checks
        }


class AlertManager:
    """
    Manages alerts based on monitoring data and predefined rules.
    """
    
    # Alert severity levels
    SEVERITY_INFO = "INFO"
    SEVERITY_WARNING = "WARNING"
    SEVERITY_ERROR = "ERROR"
    SEVERITY_CRITICAL = "CRITICAL"
    
    def __init__(self, service_name: str):
        """
        Initialize the alert manager.
        
        Args:
            service_name: Name of the service being monitored
        """
        self.service_name = service_name
        self.alert_rules = {}
        self.active_alerts = {}
        self._lock = threading.Lock()
        logger.info(f"Initialized AlertManager for service {service_name}")
    
    def register_alert_rule(self, name: str, condition_function, severity: str, 
                           description: str, remediation: Optional[str] = None) -> None:
        """
        Register a new alert rule.
        
        Args:
            name: Name of the alert rule
            condition_function: Function that evaluates if the alert should be triggered
            severity: Severity level of the alert
            description: Description of the alert
            remediation: Optional remediation steps
        """
        with self._lock:
            self.alert_rules[name] = {
                "condition": condition_function,
                "severity": severity,
                "description": description,
                "remediation": remediation
            }
        
        logger.info(f"Registered alert rule {name} with severity {severity}")
    
    def evaluate_alert_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all alert rules against the provided context.
        
        Args:
            context: Context data to evaluate rules against
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        with self._lock:
            rule_items = list(self.alert_rules.items())
        
        for name, rule in rule_items:
            try:
                # Evaluate the condition
                is_triggered, details = rule["condition"](context)
                
                if is_triggered:
                    alert_id = f"{name}-{int(time.time())}"
                    alert = {
                        "id": alert_id,
                        "name": name,
                        "service": self.service_name,
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "remediation": rule["remediation"],
                        "details": details,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "ACTIVE"
                    }
                    
                    with self._lock:
                        self.active_alerts[alert_id] = alert
                    
                    triggered_alerts.append(alert)
                    logger.warning(f"Alert triggered: {name} - {details}")
            except Exception as e:
                logger.error(f"Error evaluating alert rule {name}: {str(e)}")
        
        return triggered_alerts
    
    def resolve_alert(self, alert_id: str, resolution_details: Optional[str] = None) -> bool:
        """
        Resolve an active alert.
        
        Args:
            alert_id: ID of the alert to resolve
            resolution_details: Optional details about the resolution
            
        Returns:
            True if the alert was resolved, False otherwise
        """
        with self._lock:
            if alert_id not in self.active_alerts:
                logger.warning(f"Attempted to resolve non-existent alert with ID {alert_id}")
                return False
            
            alert = self.active_alerts[alert_id]
            alert["status"] = "RESOLVED"
            alert["resolution_time"] = datetime.utcnow().isoformat()
            alert["resolution_details"] = resolution_details
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
        
        logger.info(f"Alert {alert_id} resolved: {resolution_details}")
        return True
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active alerts, optionally filtered by severity.
        
        Args:
            severity: Optional severity level to filter by
            
        Returns:
            List of active alerts
        """
        with self._lock:
            if severity:
                return [alert for alert in self.active_alerts.values() if alert["severity"] == severity]
            else:
                return list(self.active_alerts.values())


class MonitoringSystem:
    """
    Main class that integrates all monitoring components.
    """
    
    def __init__(self, service_name: str, instance_id: Optional[str] = None):
        """
        Initialize the monitoring system.
        
        Args:
            service_name: Name of the service being monitored
            instance_id: Optional unique identifier for this service instance
        """
        self.service_name = service_name
        self.instance_id = instance_id or socket.gethostname()
        
        # Initialize components
        self.metrics = MetricsCollector(service_name, instance_id)
        self.tracer = DistributedTracer(service_name, instance_id)
        self.health = HealthChecker(service_name)
        self.alerts = AlertManager(service_name)
        
        logger.info(f"Initialized MonitoringSystem for service {service_name}, instance {self.instance_id}")
    
    def start_request_tracking(self, request_id: str, request_type: str, 
                              attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        Start tracking a request through the system.
        
        Args:
            request_id: Unique identifier for the request
            request_type: Type of request
            attributes: Optional attributes for the request
            
        Returns:
            Span ID for the request
        """
        # Create span for the request
        span_attributes = {
            "request.id": request_id,
            "request.type": request_type,
            **(attributes or {})
        }
        
        span_id = self.tracer.start_span(f"request.{request_type}", attributes=span_attributes)
        
        # Increment request counter
        self.metrics.increment_counter("requests.total", dimensions={"request_type": request_type})
        
        return span_id
    
    def end_request_tracking(self, span_id: str, status: str, 
                            duration_ms: float, attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        End tracking a request.
        
        Args:
            span_id: Span ID returned from start_request_tracking
            status: Status of the request (success, error, etc.)
            duration_ms: Duration of the request in milliseconds
            attributes: Optional additional attributes
        """
        # Record request duration
        self.metrics.record_histogram("request.duration", duration_ms, 
                                     dimensions={"status": status})
        
        # Increment status counter
        self.metrics.increment_counter(f"requests.{status.lower()}")
        
        # End the span
        self.tracer.end_span(span_id, status=status, attributes=attributes)
    
    def track_operation(self, operation_name: str, parent_span_id: Optional[str] = None):
        """
        Context manager for tracking operations within a request.
        
        Args:
            operation_name: Name of the operation
            parent_span_id: Optional parent span ID
            
        Returns:
            Context manager for the operation
        """
        class OperationTracker:
            def __init__(self, monitoring_system, operation_name, parent_span_id):
                self.monitoring_system = monitoring_system
                self.operation_name = operation_name
                self.parent_span_id = parent_span_id
                self.span_id = None
                self.start_time = None
            
            def __enter__(self):
                self.start_time = time.time()
                self.span_id = self.monitoring_system.tracer.start_span(
                    self.operation_name, parent_span_id=self.parent_span_id
                )
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                end_time = time.time()
                duration_ms = (end_time - self.start_time) * 1000
                
                status = "ERROR" if exc_type else "OK"
                attributes = {}
                
                if exc_type:
                    attributes["error.type"] = exc_type.__name__
                    attributes["error.message"] = str(exc_val)
                
                # Record operation duration
                self.monitoring_system.metrics.record_histogram(
                    f"operation.{self.operation_name}.duration", 
                    duration_ms,
                    dimensions={"status": status}
                )
                
                # End the span
                self.monitoring_system.tracer.end_span(
                    self.span_id, 
                    status=status,
                    attributes=attributes
                )
                
                # Don't suppress exceptions
                return False
            
            def add_event(self, name, attributes=None):
                """Add an event to the operation span."""
                if self.span_id:
                    self.monitoring_system.tracer.add_event(self.span_id, name, attributes)
            
            def set_attribute(self, key, value):
                """Set an attribute on the operation span."""
                if self.span_id:
                    self.monitoring_system.tracer.set_span_attribute(self.span_id, key, value)
        
        return OperationTracker(self, operation_name, parent_span_id)
    
    def get_monitoring_data(self) -> Dict[str, Any]:
        """
        Get comprehensive monitoring data.
        
        Returns:
            Dictionary containing all monitoring data
        """
        return {
            "service": self.service_name,
            "instance": self.instance_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.metrics.get_metrics(),
            "health": self.health.get_health_status(),
            "active_alerts": self.alerts.get_active_alerts(),
            "active_spans": len(self.tracer.get_active_spans())
        }


# Example usage
if __name__ == "__main__":
    # Initialize monitoring system
    monitoring = MonitoringSystem("example-service")
    
    # Register a health check
    def check_database_connection():
        # Simulate database check
        time.sleep(0.1)
        return "OK", "Database connection is healthy"
    
    monitoring.health.register_health_check("database_connection", check_database_connection)
    
    # Register an alert rule
    def check_high_error_rate(context):
        metrics = context.get("metrics", {})
        error_count = metrics.get("counters", {}).get("requests.error", 0)
        total_count = metrics.get("counters", {}).get("requests.total", 0)
        
        if total_count > 0 and error_count / total_count > 0.1:
            return True, f"Error rate is {error_count/total_count:.2%}"
        return False, None
    
    monitoring.alerts.register_alert_rule(
        "high_error_rate",
        check_high_error_rate,
        AlertManager.SEVERITY_WARNING,
        "High error rate detected",
        "Check logs for error details and investigate service health"
    )
    
    # Simulate some requests
    for i in range(10):
        # Start request tracking
        request_id = f"req-{i}"
        span_id = monitoring.start_request_tracking(request_id, "example")
        
        try:
            # Simulate request processing with nested operations
            with monitoring.track_operation("database_query", span_id) as op:
                op.add_event("query_start", {"query_type": "select"})
                time.sleep(0.05)
                op.set_attribute("rows_returned", 42)
                op.add_event("query_complete")
            
            with monitoring.track_operation("processing", span_id) as op:
                time.sleep(0.03)
                
                # Simulate an error in some requests
                if i % 3 == 0:
                    raise ValueError("Simulated error")
            
            # End request tracking (success)
            monitoring.end_request_tracking(span_id, "success", 80.0)
        except Exception as e:
            # End request tracking (error)
            monitoring.end_request_tracking(span_id, "error", 60.0, {"error": str(e)})
    
    # Run health checks
    monitoring.health.run_all_health_checks()
    
    # Evaluate alert rules
    monitoring.alerts.evaluate_alert_rules({"metrics": monitoring.metrics.get_metrics()})
    
    # Get and print monitoring data
    monitoring_data = monitoring.get_monitoring_data()
    print(json.dumps(monitoring_data, indent=2))
