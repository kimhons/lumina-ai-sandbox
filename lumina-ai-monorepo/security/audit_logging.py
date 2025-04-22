"""
Lumina AI Security Package - Audit Logging Module

This module implements comprehensive audit logging for Lumina AI, including:
- Security event logging
- User activity tracking
- System access monitoring
- Data access and modification logging
- Configuration change tracking

Copyright (c) 2025 AlienNova Technologies. All rights reserved.
"""

import uuid
import time
import json
import logging
import hashlib
import socket
import os
import threading
import queue
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union, Callable
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    USER_MANAGEMENT = "user_management"
    RESOURCE_ACCESS = "resource_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION_CHANGE = "configuration_change"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_ALERT = "security_alert"
    COMPLIANCE_EVENT = "compliance_event"
    PRIVACY_EVENT = "privacy_event"

class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditEventStatus(Enum):
    """Status of audit events."""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

@dataclass
class AuditEvent:
    """Represents an audit event in the system."""
    id: str
    timestamp: float
    event_type: AuditEventType
    severity: AuditEventSeverity
    status: AuditEventStatus
    user_id: Optional[str]
    resource_id: Optional[str]
    action: str
    source_ip: Optional[str]
    user_agent: Optional[str]
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "details": self.details,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        """Create audit event from dictionary."""
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            event_type=AuditEventType(data["event_type"]),
            severity=AuditEventSeverity(data["severity"]),
            status=AuditEventStatus(data["status"]),
            user_id=data.get("user_id"),
            resource_id=data.get("resource_id"),
            action=data["action"],
            source_ip=data.get("source_ip"),
            user_agent=data.get("user_agent"),
            details=data.get("details", {}),
            metadata=data.get("metadata", {})
        )

class AuditEventFilter:
    """Filter for querying audit events."""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.event_types: List[AuditEventType] = []
        self.severities: List[AuditEventSeverity] = []
        self.statuses: List[AuditEventStatus] = []
        self.user_ids: List[str] = []
        self.resource_ids: List[str] = []
        self.actions: List[str] = []
        self.source_ips: List[str] = []
        self.detail_filters: Dict[str, Any] = {}
        self.limit: Optional[int] = None
        self.offset: int = 0
        self.sort_by: str = "timestamp"
        self.sort_order: str = "desc"
    
    def set_time_range(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> "AuditEventFilter":
        """Set time range for filtering."""
        self.start_time = start_time
        self.end_time = end_time
        return self
    
    def add_event_type(self, event_type: AuditEventType) -> "AuditEventFilter":
        """Add event type to filter."""
        self.event_types.append(event_type)
        return self
    
    def add_severity(self, severity: AuditEventSeverity) -> "AuditEventFilter":
        """Add severity to filter."""
        self.severities.append(severity)
        return self
    
    def add_status(self, status: AuditEventStatus) -> "AuditEventFilter":
        """Add status to filter."""
        self.statuses.append(status)
        return self
    
    def add_user_id(self, user_id: str) -> "AuditEventFilter":
        """Add user ID to filter."""
        self.user_ids.append(user_id)
        return self
    
    def add_resource_id(self, resource_id: str) -> "AuditEventFilter":
        """Add resource ID to filter."""
        self.resource_ids.append(resource_id)
        return self
    
    def add_action(self, action: str) -> "AuditEventFilter":
        """Add action to filter."""
        self.actions.append(action)
        return self
    
    def add_source_ip(self, source_ip: str) -> "AuditEventFilter":
        """Add source IP to filter."""
        self.source_ips.append(source_ip)
        return self
    
    def add_detail_filter(self, key: str, value: Any) -> "AuditEventFilter":
        """Add detail filter."""
        self.detail_filters[key] = value
        return self
    
    def set_pagination(self, limit: Optional[int] = None, offset: int = 0) -> "AuditEventFilter":
        """Set pagination parameters."""
        self.limit = limit
        self.offset = offset
        return self
    
    def set_sorting(self, sort_by: str = "timestamp", sort_order: str = "desc") -> "AuditEventFilter":
        """Set sorting parameters."""
        self.sort_by = sort_by
        self.sort_order = sort_order
        return self
    
    def matches(self, event: AuditEvent) -> bool:
        """Check if an event matches this filter."""
        # Check time range
        if self.start_time is not None and event.timestamp < self.start_time:
            return False
        if self.end_time is not None and event.timestamp > self.end_time:
            return False
        
        # Check event type
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Check severity
        if self.severities and event.severity not in self.severities:
            return False
        
        # Check status
        if self.statuses and event.status not in self.statuses:
            return False
        
        # Check user ID
        if self.user_ids and (event.user_id is None or event.user_id not in self.user_ids):
            return False
        
        # Check resource ID
        if self.resource_ids and (event.resource_id is None or event.resource_id not in self.resource_ids):
            return False
        
        # Check action
        if self.actions and event.action not in self.actions:
            return False
        
        # Check source IP
        if self.source_ips and (event.source_ip is None or event.source_ip not in self.source_ips):
            return False
        
        # Check detail filters
        for key, value in self.detail_filters.items():
            if key not in event.details or event.details[key] != value:
                return False
        
        return True

class AuditEventStorage:
    """Interface for audit event storage."""
    
    def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event."""
        raise NotImplementedError("Subclasses must implement store_event")
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get an audit event by ID."""
        raise NotImplementedError("Subclasses must implement get_event")
    
    def query_events(self, filter: AuditEventFilter) -> List[AuditEvent]:
        """Query audit events using a filter."""
        raise NotImplementedError("Subclasses must implement query_events")
    
    def count_events(self, filter: AuditEventFilter) -> int:
        """Count audit events matching a filter."""
        raise NotImplementedError("Subclasses must implement count_events")
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an audit event."""
        raise NotImplementedError("Subclasses must implement delete_event")
    
    def delete_events(self, filter: AuditEventFilter) -> int:
        """Delete audit events matching a filter."""
        raise NotImplementedError("Subclasses must implement delete_events")

class InMemoryAuditEventStorage(AuditEventStorage):
    """In-memory implementation of audit event storage."""
    
    def __init__(self):
        self.events: Dict[str, AuditEvent] = {}
    
    def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event."""
        self.events[event.id] = event
        return True
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get an audit event by ID."""
        return self.events.get(event_id)
    
    def query_events(self, filter: AuditEventFilter) -> List[AuditEvent]:
        """Query audit events using a filter."""
        # Filter events
        filtered_events = [event for event in self.events.values() if filter.matches(event)]
        
        # Sort events
        reverse = filter.sort_order.lower() == "desc"
        filtered_events.sort(key=lambda e: getattr(e, filter.sort_by), reverse=reverse)
        
        # Apply pagination
        if filter.offset > 0:
            filtered_events = filtered_events[filter.offset:]
        
        if filter.limit is not None:
            filtered_events = filtered_events[:filter.limit]
        
        return filtered_events
    
    def count_events(self, filter: AuditEventFilter) -> int:
        """Count audit events matching a filter."""
        return len([event for event in self.events.values() if filter.matches(event)])
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an audit event."""
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False
    
    def delete_events(self, filter: AuditEventFilter) -> int:
        """Delete audit events matching a filter."""
        to_delete = [event.id for event in self.events.values() if filter.matches(event)]
        for event_id in to_delete:
            del self.events[event_id]
        return len(to_delete)

class FileAuditEventStorage(AuditEventStorage):
    """File-based implementation of audit event storage."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.events: Dict[str, AuditEvent] = {}
        self.load_events()
    
    def load_events(self) -> None:
        """Load events from file."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for event_data in data:
                        event = AuditEvent.from_dict(event_data)
                        self.events[event.id] = event
                logger.info(f"Loaded {len(self.events)} audit events from {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to load audit events from {self.file_path}: {e}")
    
    def save_events(self) -> None:
        """Save events to file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump([event.to_dict() for event in self.events.values()], f, indent=2)
            logger.info(f"Saved {len(self.events)} audit events to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save audit events to {self.file_path}: {e}")
    
    def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event."""
        self.events[event.id] = event
        self.save_events()
        return True
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get an audit event by ID."""
        return self.events.get(event_id)
    
    def query_events(self, filter: AuditEventFilter) -> List[AuditEvent]:
        """Query audit events using a filter."""
        # Filter events
        filtered_events = [event for event in self.events.values() if filter.matches(event)]
        
        # Sort events
        reverse = filter.sort_order.lower() == "desc"
        filtered_events.sort(key=lambda e: getattr(e, filter.sort_by), reverse=reverse)
        
        # Apply pagination
        if filter.offset > 0:
            filtered_events = filtered_events[filter.offset:]
        
        if filter.limit is not None:
            filtered_events = filtered_events[:filter.limit]
        
        return filtered_events
    
    def count_events(self, filter: AuditEventFilter) -> int:
        """Count audit events matching a filter."""
        return len([event for event in self.events.values() if filter.matches(event)])
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an audit event."""
        if event_id in self.events:
            del self.events[event_id]
            self.save_events()
            return True
        return False
    
    def delete_events(self, filter: AuditEventFilter) -> int:
        """Delete audit events matching a filter."""
        to_delete = [event.id for event in self.events.values() if filter.matches(event)]
        for event_id in to_delete:
            del self.events[event_id]
        self.save_events()
        return len(to_delete)

class AsyncAuditEventProcessor:
    """Asynchronous processor for audit events."""
    
    def __init__(self, storage: AuditEventStorage):
        self.storage = storage
        self.event_queue = queue.Queue()
        self.running = False
        self.worker_thread = None
    
    def start(self) -> None:
        """Start the event processor."""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_events)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        logger.info("Started async audit event processor")
    
    def stop(self) -> None:
        """Stop the event processor."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            self.worker_thread = None
        logger.info("Stopped async audit event processor")
    
    def submit_event(self, event: AuditEvent) -> None:
        """Submit an event for processing."""
        self.event_queue.put(event)
    
    def _process_events(self) -> None:
        """Process events from the queue."""
        while self.running:
            try:
                # Get event from queue with timeout to allow checking running flag
                try:
                    event = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Store event
                try:
                    self.storage.store_event(event)
                except Exception as e:
                    logger.error(f"Failed to store audit event: {e}")
                
                # Mark task as done
                self.event_queue.task_done()
            except Exception as e:
                logger.error(f"Error in audit event processor: {e}")

class AuditLogger:
    """Main class for audit logging."""
    
    def __init__(self, storage: AuditEventStorage, async_processing: bool = True):
        self.storage = storage
        self.async_processing = async_processing
        self.processor = AsyncAuditEventProcessor(storage) if async_processing else None
        self.hostname = socket.gethostname()
        
        if self.async_processing:
            self.processor.start()
    
    def log_event(self, event_type: AuditEventType, severity: AuditEventSeverity, status: AuditEventStatus,
                 user_id: Optional[str], resource_id: Optional[str], action: str,
                 source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                 details: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> str:
        """Log an audit event."""
        # Create event
        event_id = str(uuid.uuid4())
        event = AuditEvent(
            id=event_id,
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            status=status,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            source_ip=source_ip,
            user_agent=user_agent,
            details=details or {},
            metadata=metadata or {}
        )
        
        # Add system metadata
        event.metadata["hostname"] = self.hostname
        event.metadata["process_id"] = os.getpid()
        
        # Process event
        if self.async_processing:
            self.processor.submit_event(event)
        else:
            self.storage.store_event(event)
        
        return event_id
    
    def log_authentication(self, user_id: str, status: AuditEventStatus, auth_method: str,
                          source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                          details: Dict[str, Any] = None) -> str:
        """Log an authentication event."""
        event_details = details or {}
        event_details["auth_method"] = auth_method
        
        severity = AuditEventSeverity.MEDIUM if status == AuditEventStatus.FAILURE else AuditEventSeverity.INFO
        
        return self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            severity=severity,
            status=status,
            user_id=user_id,
            resource_id=None,
            action=f"authentication_{status.value}",
            source_ip=source_ip,
            user_agent=user_agent,
            details=event_details
        )
    
    def log_authorization(self, user_id: str, resource_id: str, action: str, status: AuditEventStatus,
                         source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                         details: Dict[str, Any] = None) -> str:
        """Log an authorization event."""
        severity = AuditEventSeverity.MEDIUM if status == AuditEventStatus.FAILURE else AuditEventSeverity.INFO
        
        return self.log_event(
            event_type=AuditEventType.AUTHORIZATION,
            severity=severity,
            status=status,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            source_ip=source_ip,
            user_agent=user_agent,
            details=details
        )
    
    def log_user_management(self, admin_user_id: str, target_user_id: str, action: str,
                           source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                           details: Dict[str, Any] = None) -> str:
        """Log a user management event."""
        event_details = details or {}
        event_details["target_user_id"] = target_user_id
        
        return self.log_event(
            event_type=AuditEventType.USER_MANAGEMENT,
            severity=AuditEventSeverity.MEDIUM,
            status=AuditEventStatus.SUCCESS,
            user_id=admin_user_id,
            resource_id=None,
            action=action,
            source_ip=source_ip,
            user_agent=user_agent,
            details=event_details
        )
    
    def log_resource_access(self, user_id: str, resource_id: str, action: str,
                           source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                           details: Dict[str, Any] = None) -> str:
        """Log a resource access event."""
        return self.log_event(
            event_type=AuditEventType.RESOURCE_ACCESS,
            severity=AuditEventSeverity.INFO,
            status=AuditEventStatus.SUCCESS,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            source_ip=source_ip,
            user_agent=user_agent,
            details=details
        )
    
    def log_data_modification(self, user_id: str, resource_id: str, action: str,
                             source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                             details: Dict[str, Any] = None) -> str:
        """Log a data modification event."""
        return self.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditEventSeverity.MEDIUM,
            status=AuditEventStatus.SUCCESS,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            source_ip=source_ip,
            user_agent=user_agent,
            details=details
        )
    
    def log_configuration_change(self, user_id: str, component: str, action: str,
                                source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                                details: Dict[str, Any] = None) -> str:
        """Log a configuration change event."""
        event_details = details or {}
        event_details["component"] = component
        
        return self.log_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            severity=AuditEventSeverity.MEDIUM,
            status=AuditEventStatus.SUCCESS,
            user_id=user_id,
            resource_id=None,
            action=action,
            source_ip=source_ip,
            user_agent=user_agent,
            details=event_details
        )
    
    def log_system_operation(self, user_id: Optional[str], operation: str, status: AuditEventStatus,
                            details: Dict[str, Any] = None) -> str:
        """Log a system operation event."""
        return self.log_event(
            event_type=AuditEventType.SYSTEM_OPERATION,
            severity=AuditEventSeverity.INFO,
            status=status,
            user_id=user_id,
            resource_id=None,
            action=operation,
            details=details
        )
    
    def log_security_alert(self, severity: AuditEventSeverity, alert_type: str, details: Dict[str, Any] = None,
                          user_id: Optional[str] = None, resource_id: Optional[str] = None,
                          source_ip: Optional[str] = None) -> str:
        """Log a security alert event."""
        event_details = details or {}
        event_details["alert_type"] = alert_type
        
        return self.log_event(
            event_type=AuditEventType.SECURITY_ALERT,
            severity=severity,
            status=AuditEventStatus.WARNING,
            user_id=user_id,
            resource_id=resource_id,
            action="security_alert",
            source_ip=source_ip,
            details=event_details
        )
    
    def log_compliance_event(self, regulation: str, requirement: str, status: AuditEventStatus,
                            details: Dict[str, Any] = None) -> str:
        """Log a compliance event."""
        event_details = details or {}
        event_details["regulation"] = regulation
        event_details["requirement"] = requirement
        
        severity = AuditEventSeverity.HIGH if status == AuditEventStatus.FAILURE else AuditEventSeverity.MEDIUM
        
        return self.log_event(
            event_type=AuditEventType.COMPLIANCE_EVENT,
            severity=severity,
            status=status,
            user_id=None,
            resource_id=None,
            action="compliance_check",
            details=event_details
        )
    
    def log_privacy_event(self, user_id: Optional[str], data_category: str, action: str,
                         details: Dict[str, Any] = None) -> str:
        """Log a privacy event."""
        event_details = details or {}
        event_details["data_category"] = data_category
        
        return self.log_event(
            event_type=AuditEventType.PRIVACY_EVENT,
            severity=AuditEventSeverity.MEDIUM,
            status=AuditEventStatus.INFO,
            user_id=user_id,
            resource_id=None,
            action=action,
            details=event_details
        )
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get an audit event by ID."""
        return self.storage.get_event(event_id)
    
    def query_events(self, filter: AuditEventFilter) -> List[AuditEvent]:
        """Query audit events using a filter."""
        return self.storage.query_events(filter)
    
    def count_events(self, filter: AuditEventFilter) -> int:
        """Count audit events matching a filter."""
        return self.storage.count_events(filter)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an audit event."""
        return self.storage.delete_event(event_id)
    
    def delete_events(self, filter: AuditEventFilter) -> int:
        """Delete audit events matching a filter."""
        return self.storage.delete_events(filter)
    
    def shutdown(self) -> None:
        """Shut down the audit logger."""
        if self.async_processing and self.processor:
            self.processor.stop()
            logger.info("Audit logger shut down")
