"""
Analytics and Insights Platform for Lumina AI

This module provides comprehensive analytics capabilities for Lumina AI,
including usage analytics, user behavior insights, performance analytics,
cost analytics, AI provider analytics, and business impact metrics.
"""

import logging
import time
import os
import json
import threading
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
import hashlib
import uuid
import csv
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventCollector:
    """
    Collects and processes analytics events from various sources.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize the event collector.
        
        Args:
            service_name: Name of the service collecting events
        """
        self.service_name = service_name
        self.events = []
        self.event_handlers = {}
        self._lock = threading.Lock()
        logger.info(f"Initialized EventCollector for service {service_name}")
    
    def track_event(self, event_type: str, user_id: Optional[str] = None, 
                   properties: Optional[Dict[str, Any]] = None) -> str:
        """
        Track an analytics event.
        
        Args:
            event_type: Type of event
            user_id: Optional user identifier
            properties: Optional event properties
            
        Returns:
            Unique event ID
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        event = {
            "id": event_id,
            "type": event_type,
            "user_id": user_id,
            "service": self.service_name,
            "timestamp": timestamp,
            "properties": properties or {}
        }
        
        with self._lock:
            self.events.append(event)
            
            # Limit the number of events stored in memory
            if len(self.events) > 10000:
                self.events = self.events[-10000:]
            
            # Call event handlers
            handlers = self.event_handlers.get(event_type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")
        
        logger.debug(f"Tracked event {event_type} with ID {event_id}")
        return event_id
    
    def register_event_handler(self, event_type: str, handler_func: Callable) -> None:
        """
        Register a handler function for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler_func: Function to call when event occurs
        """
        with self._lock:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(handler_func)
        
        logger.info(f"Registered handler for event type {event_type}")
    
    def get_events(self, event_type: Optional[str] = None, 
                  user_id: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get events matching the specified criteria.
        
        Args:
            event_type: Optional event type to filter by
            user_id: Optional user ID to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        with self._lock:
            filtered_events = self.events.copy()
        
        # Apply filters
        if event_type:
            filtered_events = [e for e in filtered_events if e["type"] == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e["user_id"] == user_id]
        
        if start_time:
            start_str = start_time.isoformat()
            filtered_events = [e for e in filtered_events if e["timestamp"] >= start_str]
        
        if end_time:
            end_str = end_time.isoformat()
            filtered_events = [e for e in filtered_events if e["timestamp"] <= end_str]
        
        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda e: e["timestamp"], reverse=True)
        
        # Apply limit
        return filtered_events[:limit]
    
    def export_events_csv(self, event_type: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> str:
        """
        Export events to CSV format.
        
        Args:
            event_type: Optional event type to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            CSV string containing events
        """
        events = self.get_events(event_type=event_type, start_time=start_time, 
                                end_time=end_time, limit=100000)
        
        if not events:
            return "No events found"
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = ["id", "type", "user_id", "service", "timestamp"]
        
        # Add property columns (from first event)
        property_keys = list(events[0]["properties"].keys())
        header.extend(property_keys)
        
        writer.writerow(header)
        
        # Write data rows
        for event in events:
            row = [
                event["id"],
                event["type"],
                event["user_id"],
                event["service"],
                event["timestamp"]
            ]
            
            # Add property values
            for key in property_keys:
                row.append(event["properties"].get(key, ""))
            
            writer.writerow(row)
        
        return output.getvalue()


class UserAnalytics:
    """
    Analyzes user behavior and interaction patterns.
    """
    
    def __init__(self, event_collector: EventCollector):
        """
        Initialize the user analytics.
        
        Args:
            event_collector: Event collector to use for tracking events
        """
        self.event_collector = event_collector
        logger.info("Initialized UserAnalytics")
    
    def track_user_session(self, user_id: str, session_id: str, 
                          session_start: bool = False, session_end: bool = False,
                          duration_seconds: Optional[float] = None,
                          properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a user session event.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            session_start: Whether this is a session start event
            session_end: Whether this is a session end event
            duration_seconds: Optional session duration (for end events)
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties.update({
            "session_id": session_id,
            "session_start": session_start,
            "session_end": session_end
        })
        
        if duration_seconds is not None:
            event_properties["duration_seconds"] = duration_seconds
        
        self.event_collector.track_event("user_session", user_id, event_properties)
    
    def track_user_action(self, user_id: str, action_type: str, 
                         session_id: Optional[str] = None,
                         properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a user action event.
        
        Args:
            user_id: User identifier
            action_type: Type of action
            session_id: Optional session identifier
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties["action_type"] = action_type
        
        if session_id:
            event_properties["session_id"] = session_id
        
        self.event_collector.track_event("user_action", user_id, event_properties)
    
    def track_feature_usage(self, user_id: str, feature_id: str, 
                           session_id: Optional[str] = None,
                           properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track feature usage event.
        
        Args:
            user_id: User identifier
            feature_id: Feature identifier
            session_id: Optional session identifier
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties["feature_id"] = feature_id
        
        if session_id:
            event_properties["session_id"] = session_id
        
        self.event_collector.track_event("feature_usage", user_id, event_properties)
    
    def get_user_sessions(self, user_id: str, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get sessions for a specific user.
        
        Args:
            user_id: User identifier
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            limit: Maximum number of sessions to return
            
        Returns:
            List of user sessions
        """
        # Get session events for the user
        events = self.event_collector.get_events(
            event_type="user_session",
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit * 2  # Get more events to account for start/end pairs
        )
        
        # Group by session ID
        sessions = {}
        for event in events:
            session_id = event["properties"].get("session_id")
            if not session_id:
                continue
            
            if session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "start_time": None,
                    "end_time": None,
                    "duration_seconds": None,
                    "properties": {}
                }
            
            # Update session data
            if event["properties"].get("session_start"):
                sessions[session_id]["start_time"] = event["timestamp"]
                # Copy properties from start event
                for key, value in event["properties"].items():
                    if key not in ["session_id", "session_start", "session_end"]:
                        sessions[session_id]["properties"][key] = value
            
            if event["properties"].get("session_end"):
                sessions[session_id]["end_time"] = event["timestamp"]
                if "duration_seconds" in event["properties"]:
                    sessions[session_id]["duration_seconds"] = event["properties"]["duration_seconds"]
        
        # Convert to list and sort by start time (newest first)
        session_list = list(sessions.values())
        session_list.sort(key=lambda s: s["start_time"] if s["start_time"] else "", reverse=True)
        
        return session_list[:limit]
    
    def get_user_actions(self, user_id: str, 
                        action_type: Optional[str] = None,
                        session_id: Optional[str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get actions for a specific user.
        
        Args:
            user_id: User identifier
            action_type: Optional action type to filter by
            session_id: Optional session ID to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            limit: Maximum number of actions to return
            
        Returns:
            List of user actions
        """
        # Get action events for the user
        events = self.event_collector.get_events(
            event_type="user_action",
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        # Filter by action type and session ID
        filtered_actions = []
        for event in events:
            if action_type and event["properties"].get("action_type") != action_type:
                continue
            
            if session_id and event["properties"].get("session_id") != session_id:
                continue
            
            action = {
                "id": event["id"],
                "user_id": user_id,
                "timestamp": event["timestamp"],
                "action_type": event["properties"].get("action_type"),
                "session_id": event["properties"].get("session_id"),
                "properties": {k: v for k, v in event["properties"].items() 
                              if k not in ["action_type", "session_id"]}
            }
            
            filtered_actions.append(action)
        
        return filtered_actions
    
    def get_feature_usage(self, feature_id: Optional[str] = None,
                         user_id: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get feature usage statistics.
        
        Args:
            feature_id: Optional feature ID to filter by
            user_id: Optional user ID to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            Feature usage statistics
        """
        # Get feature usage events
        events = self.event_collector.get_events(
            event_type="feature_usage",
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        # Filter by feature ID
        if feature_id:
            events = [e for e in events if e["properties"].get("feature_id") == feature_id]
        
        # Count usage by feature
        feature_counts = {}
        user_counts = {}
        session_counts = {}
        
        for event in events:
            feat_id = event["properties"].get("feature_id", "unknown")
            user = event["user_id"] or "anonymous"
            session = event["properties"].get("session_id", "unknown")
            
            # Count by feature
            if feat_id not in feature_counts:
                feature_counts[feat_id] = 0
            feature_counts[feat_id] += 1
            
            # Count unique users by feature
            if feat_id not in user_counts:
                user_counts[feat_id] = set()
            user_counts[feat_id].add(user)
            
            # Count unique sessions by feature
            if feat_id not in session_counts:
                session_counts[feat_id] = set()
            session_counts[feat_id].add(session)
        
        # Prepare results
        results = {
            "total_usage": len(events),
            "unique_users": len(set(e["user_id"] for e in events if e["user_id"])),
            "unique_sessions": len(set(e["properties"].get("session_id") 
                                     for e in events if e["properties"].get("session_id"))),
            "features": []
        }
        
        # Add feature-specific stats
        for feat_id, count in feature_counts.items():
            results["features"].append({
                "feature_id": feat_id,
                "usage_count": count,
                "unique_users": len(user_counts.get(feat_id, set())),
                "unique_sessions": len(session_counts.get(feat_id, set()))
            })
        
        # Sort by usage count (descending)
        results["features"].sort(key=lambda f: f["usage_count"], reverse=True)
        
        return results


class PerformanceAnalytics:
    """
    Analyzes performance metrics and trends.
    """
    
    def __init__(self, event_collector: EventCollector):
        """
        Initialize the performance analytics.
        
        Args:
            event_collector: Event collector to use for tracking events
        """
        self.event_collector = event_collector
        logger.info("Initialized PerformanceAnalytics")
    
    def track_api_request(self, endpoint: str, method: str, status_code: int,
                         duration_ms: float, user_id: Optional[str] = None,
                         properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an API request event.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: Optional user identifier
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties.update({
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms
        })
        
        self.event_collector.track_event("api_request", user_id, event_properties)
    
    def track_model_inference(self, model_id: str, provider: str,
                            duration_ms: float, token_count: int,
                            success: bool, user_id: Optional[str] = None,
                            properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a model inference event.
        
        Args:
            model_id: Model identifier
            provider: AI provider name
            duration_ms: Inference duration in milliseconds
            token_count: Number of tokens processed
            success: Whether the inference was successful
            user_id: Optional user identifier
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties.update({
            "model_id": model_id,
            "provider": provider,
            "duration_ms": duration_ms,
            "token_count": token_count,
            "success": success
        })
        
        self.event_collector.track_event("model_inference", user_id, event_properties)
    
    def track_resource_usage(self, resource_type: str, resource_id: str,
                           usage_value: float, usage_unit: str,
                           properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a resource usage event.
        
        Args:
            resource_type: Type of resource (cpu, memory, disk, etc.)
            resource_id: Resource identifier
            usage_value: Usage value
            usage_unit: Unit of measurement
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties.update({
            "resource_type": resource_type,
            "resource_id": resource_id,
            "usage_value": usage_value,
            "usage_unit": usage_unit
        })
        
        self.event_collector.track_event("resource_usage", None, event_properties)
    
    def get_api_performance(self, endpoint: Optional[str] = None,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get API performance statistics.
        
        Args:
            endpoint: Optional endpoint to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            API performance statistics
        """
        # Get API request events
        events = self.event_collector.get_events(
            event_type="api_request",
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        # Filter by endpoint
        if endpoint:
            events = [e for e in events if e["properties"].get("endpoint") == endpoint]
        
        if not events:
            return {"total_requests": 0, "endpoints": []}
        
        # Group by endpoint
        endpoints = {}
        for event in events:
            ep = event["properties"].get("endpoint", "unknown")
            status = event["properties"].get("status_code", 0)
            duration = event["properties"].get("duration_ms", 0)
            
            if ep not in endpoints:
                endpoints[ep] = {
                    "endpoint": ep,
                    "total_requests": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "durations": []
                }
            
            endpoints[ep]["total_requests"] += 1
            endpoints[ep]["durations"].append(duration)
            
            if 200 <= status < 400:
                endpoints[ep]["success_count"] += 1
            else:
                endpoints[ep]["error_count"] += 1
        
        # Calculate statistics for each endpoint
        for ep_data in endpoints.values():
            durations = ep_data["durations"]
            ep_data["avg_duration_ms"] = sum(durations) / len(durations)
            ep_data["min_duration_ms"] = min(durations)
            ep_data["max_duration_ms"] = max(durations)
            ep_data["p95_duration_ms"] = sorted(durations)[int(len(durations) * 0.95)]
            ep_data["error_rate"] = ep_data["error_count"] / ep_data["total_requests"] if ep_data["total_requests"] > 0 else 0
            del ep_data["durations"]  # Remove raw durations from result
        
        # Prepare results
        results = {
            "total_requests": len(events),
            "success_count": sum(1 for e in events if 200 <= e["properties"].get("status_code", 0) < 400),
            "error_count": sum(1 for e in events if not (200 <= e["properties"].get("status_code", 0) < 400)),
            "avg_duration_ms": sum(e["properties"].get("duration_ms", 0) for e in events) / len(events),
            "endpoints": list(endpoints.values())
        }
        
        # Sort endpoints by total requests (descending)
        results["endpoints"].sort(key=lambda e: e["total_requests"], reverse=True)
        
        return results
    
    def get_model_performance(self, model_id: Optional[str] = None,
                            provider: Optional[str] = None,
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get model inference performance statistics.
        
        Args:
            model_id: Optional model ID to filter by
            provider: Optional provider to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            Model performance statistics
        """
        # Get model inference events
        events = self.event_collector.get_events(
            event_type="model_inference",
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        # Apply filters
        if model_id:
            events = [e for e in events if e["properties"].get("model_id") == model_id]
        
        if provider:
            events = [e for e in events if e["properties"].get("provider") == provider]
        
        if not events:
            return {"total_inferences": 0, "models": []}
        
        # Group by model and provider
        models = {}
        for event in events:
            model = event["properties"].get("model_id", "unknown")
            prov = event["properties"].get("provider", "unknown")
            key = f"{prov}:{model}"
            
            success = event["properties"].get("success", False)
            duration = event["properties"].get("duration_ms", 0)
            tokens = event["properties"].get("token_count", 0)
            
            if key not in models:
                models[key] = {
                    "model_id": model,
                    "provider": prov,
                    "total_inferences": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "durations": [],
                    "token_counts": []
                }
            
            models[key]["total_inferences"] += 1
            models[key]["durations"].append(duration)
            models[key]["token_counts"].append(tokens)
            
            if success:
                models[key]["success_count"] += 1
            else:
                models[key]["error_count"] += 1
        
        # Calculate statistics for each model
        for model_data in models.values():
            durations = model_data["durations"]
            tokens = model_data["token_counts"]
            
            model_data["avg_duration_ms"] = sum(durations) / len(durations)
            model_data["min_duration_ms"] = min(durations)
            model_data["max_duration_ms"] = max(durations)
            model_data["p95_duration_ms"] = sorted(durations)[int(len(durations) * 0.95)]
            
            model_data["avg_token_count"] = sum(tokens) / len(tokens)
            model_data["total_token_count"] = sum(tokens)
            
            model_data["tokens_per_second"] = (model_data["total_token_count"] * 1000) / sum(durations) if sum(durations) > 0 else 0
            model_data["error_rate"] = model_data["error_count"] / model_data["total_inferences"] if model_data["total_inferences"] > 0 else 0
            
            del model_data["durations"]
            del model_data["token_counts"]
        
        # Prepare results
        results = {
            "total_inferences": len(events),
            "success_count": sum(1 for e in events if e["properties"].get("success", False)),
            "error_count": sum(1 for e in events if not e["properties"].get("success", False)),
            "avg_duration_ms": sum(e["properties"].get("duration_ms", 0) for e in events) / len(events),
            "total_token_count": sum(e["properties"].get("token_count", 0) for e in events),
            "models": list(models.values())
        }
        
        # Sort models by total inferences (descending)
        results["models"].sort(key=lambda m: m["total_inferences"], reverse=True)
        
        return results
    
    def get_resource_usage_trends(self, resource_type: Optional[str] = None,
                                resource_id: Optional[str] = None,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None,
                                interval_minutes: int = 60) -> Dict[str, Any]:
        """
        Get resource usage trends over time.
        
        Args:
            resource_type: Optional resource type to filter by
            resource_id: Optional resource ID to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            interval_minutes: Time interval for aggregation in minutes
            
        Returns:
            Resource usage trends
        """
        # Get resource usage events
        events = self.event_collector.get_events(
            event_type="resource_usage",
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        # Apply filters
        if resource_type:
            events = [e for e in events if e["properties"].get("resource_type") == resource_type]
        
        if resource_id:
            events = [e for e in events if e["properties"].get("resource_id") == resource_id]
        
        if not events:
            return {"resources": []}
        
        # Determine time range
        if start_time is None:
            start_time = datetime.fromisoformat(min(e["timestamp"] for e in events).split("+")[0])
        
        if end_time is None:
            end_time = datetime.fromisoformat(max(e["timestamp"] for e in events).split("+")[0])
        
        # Create time intervals
        interval_delta = timedelta(minutes=interval_minutes)
        intervals = []
        
        current_time = start_time
        while current_time <= end_time:
            intervals.append({
                "start": current_time,
                "end": current_time + interval_delta,
                "data": {}
            })
            current_time += interval_delta
        
        # Group by resource type and ID
        resources = {}
        for event in events:
            res_type = event["properties"].get("resource_type", "unknown")
            res_id = event["properties"].get("resource_id", "unknown")
            key = f"{res_type}:{res_id}"
            
            if key not in resources:
                resources[key] = {
                    "resource_type": res_type,
                    "resource_id": res_id,
                    "unit": event["properties"].get("usage_unit", ""),
                    "intervals": []
                }
        
        # Populate intervals for each resource
        for key, resource in resources.items():
            # Initialize intervals
            resource["intervals"] = [
                {
                    "start_time": interval["start"].isoformat(),
                    "end_time": interval["end"].isoformat(),
                    "values": []
                }
                for interval in intervals
            ]
            
            # Add data points to intervals
            for event in events:
                if (event["properties"].get("resource_type") == resource["resource_type"] and
                    event["properties"].get("resource_id") == resource["resource_id"]):
                    
                    event_time = datetime.fromisoformat(event["timestamp"].split("+")[0])
                    value = event["properties"].get("usage_value", 0)
                    
                    # Find the right interval
                    for i, interval in enumerate(intervals):
                        if interval["start"] <= event_time < interval["end"]:
                            resource["intervals"][i]["values"].append(value)
                            break
            
            # Calculate statistics for each interval
            for interval in resource["intervals"]:
                values = interval["values"]
                if values:
                    interval["avg_value"] = sum(values) / len(values)
                    interval["min_value"] = min(values)
                    interval["max_value"] = max(values)
                    interval["count"] = len(values)
                else:
                    interval["avg_value"] = 0
                    interval["min_value"] = 0
                    interval["max_value"] = 0
                    interval["count"] = 0
                
                del interval["values"]  # Remove raw values from result
        
        return {"resources": list(resources.values())}


class CostAnalytics:
    """
    Analyzes operational costs and optimization opportunities.
    """
    
    def __init__(self, event_collector: EventCollector):
        """
        Initialize the cost analytics.
        
        Args:
            event_collector: Event collector to use for tracking events
        """
        self.event_collector = event_collector
        logger.info("Initialized CostAnalytics")
    
    def track_cost_event(self, cost_type: str, amount: float, currency: str = "USD",
                        resource_id: Optional[str] = None, user_id: Optional[str] = None,
                        properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a cost event.
        
        Args:
            cost_type: Type of cost (api, compute, storage, etc.)
            amount: Cost amount
            currency: Currency code
            resource_id: Optional resource identifier
            user_id: Optional user identifier
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties.update({
            "cost_type": cost_type,
            "amount": amount,
            "currency": currency
        })
        
        if resource_id:
            event_properties["resource_id"] = resource_id
        
        self.event_collector.track_event("cost", user_id, event_properties)
    
    def track_api_cost(self, provider: str, model_id: str, token_count: int,
                     cost_per_1k_tokens: float, user_id: Optional[str] = None,
                     properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an API cost event.
        
        Args:
            provider: AI provider name
            model_id: Model identifier
            token_count: Number of tokens processed
            cost_per_1k_tokens: Cost per 1,000 tokens
            user_id: Optional user identifier
            properties: Optional additional properties
        """
        # Calculate cost
        cost_amount = (token_count / 1000) * cost_per_1k_tokens
        
        event_properties = properties or {}
        event_properties.update({
            "provider": provider,
            "model_id": model_id,
            "token_count": token_count,
            "cost_per_1k_tokens": cost_per_1k_tokens
        })
        
        self.track_cost_event("api", cost_amount, "USD", f"{provider}:{model_id}", user_id, event_properties)
    
    def get_cost_summary(self, cost_type: Optional[str] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       group_by: str = "cost_type") -> Dict[str, Any]:
        """
        Get cost summary statistics.
        
        Args:
            cost_type: Optional cost type to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            group_by: Field to group costs by (cost_type, resource_id, user_id)
            
        Returns:
            Cost summary statistics
        """
        # Get cost events
        events = self.event_collector.get_events(
            event_type="cost",
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        # Filter by cost type
        if cost_type:
            events = [e for e in events if e["properties"].get("cost_type") == cost_type]
        
        if not events:
            return {"total_cost": 0, "currency": "USD", "groups": []}
        
        # Determine currency (assuming all events use the same currency)
        currency = events[0]["properties"].get("currency", "USD")
        
        # Group by specified field
        groups = {}
        for event in events:
            # Get group key
            if group_by == "cost_type":
                key = event["properties"].get("cost_type", "unknown")
            elif group_by == "resource_id":
                key = event["properties"].get("resource_id", "unknown")
            elif group_by == "user_id":
                key = event["user_id"] or "anonymous"
            else:
                key = "all"
            
            amount = event["properties"].get("amount", 0)
            
            if key not in groups:
                groups[key] = {
                    "key": key,
                    "total_cost": 0,
                    "event_count": 0
                }
            
            groups[key]["total_cost"] += amount
            groups[key]["event_count"] += 1
        
        # Calculate total cost
        total_cost = sum(g["total_cost"] for g in groups.values())
        
        # Add percentage to each group
        for group in groups.values():
            group["percentage"] = (group["total_cost"] / total_cost * 100) if total_cost > 0 else 0
        
        # Prepare results
        results = {
            "total_cost": total_cost,
            "currency": currency,
            "event_count": len(events),
            "group_by": group_by,
            "groups": list(groups.values())
        }
        
        # Sort groups by total cost (descending)
        results["groups"].sort(key=lambda g: g["total_cost"], reverse=True)
        
        return results
    
    def get_api_cost_analysis(self, provider: Optional[str] = None,
                            model_id: Optional[str] = None,
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get API cost analysis.
        
        Args:
            provider: Optional provider to filter by
            model_id: Optional model ID to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            API cost analysis
        """
        # Get API cost events
        events = self.event_collector.get_events(
            event_type="cost",
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        # Filter to API costs only
        events = [e for e in events if e["properties"].get("cost_type") == "api"]
        
        # Apply additional filters
        if provider:
            events = [e for e in events if e["properties"].get("provider") == provider]
        
        if model_id:
            events = [e for e in events if e["properties"].get("model_id") == model_id]
        
        if not events:
            return {"total_cost": 0, "currency": "USD", "models": []}
        
        # Determine currency
        currency = events[0]["properties"].get("currency", "USD")
        
        # Group by provider and model
        models = {}
        for event in events:
            prov = event["properties"].get("provider", "unknown")
            model = event["properties"].get("model_id", "unknown")
            key = f"{prov}:{model}"
            
            amount = event["properties"].get("amount", 0)
            tokens = event["properties"].get("token_count", 0)
            
            if key not in models:
                models[key] = {
                    "provider": prov,
                    "model_id": model,
                    "total_cost": 0,
                    "total_tokens": 0,
                    "request_count": 0
                }
            
            models[key]["total_cost"] += amount
            models[key]["total_tokens"] += tokens
            models[key]["request_count"] += 1
        
        # Calculate additional metrics for each model
        for model_data in models.values():
            model_data["avg_cost_per_request"] = model_data["total_cost"] / model_data["request_count"] if model_data["request_count"] > 0 else 0
            model_data["avg_tokens_per_request"] = model_data["total_tokens"] / model_data["request_count"] if model_data["request_count"] > 0 else 0
            model_data["effective_cost_per_1k_tokens"] = (model_data["total_cost"] / model_data["total_tokens"] * 1000) if model_data["total_tokens"] > 0 else 0
        
        # Calculate total cost
        total_cost = sum(m["total_cost"] for m in models.values())
        total_tokens = sum(m["total_tokens"] for m in models.values())
        
        # Add percentage to each model
        for model_data in models.values():
            model_data["percentage"] = (model_data["total_cost"] / total_cost * 100) if total_cost > 0 else 0
        
        # Prepare results
        results = {
            "total_cost": total_cost,
            "currency": currency,
            "total_tokens": total_tokens,
            "request_count": sum(m["request_count"] for m in models.values()),
            "avg_cost_per_1k_tokens": (total_cost / total_tokens * 1000) if total_tokens > 0 else 0,
            "models": list(models.values())
        }
        
        # Sort models by total cost (descending)
        results["models"].sort(key=lambda m: m["total_cost"], reverse=True)
        
        return results
    
    def get_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get cost optimization recommendations.
        
        Returns:
            List of cost optimization recommendations
        """
        recommendations = []
        
        # Analyze API costs
        api_costs = self.get_api_cost_analysis(
            start_time=datetime.utcnow() - timedelta(days=30)
        )
        
        # Check for expensive models
        for model in api_costs.get("models", []):
            if model["effective_cost_per_1k_tokens"] > 0.01 and model["total_tokens"] > 10000:
                # Find cheaper alternatives
                cheaper_alternatives = [
                    m for m in api_costs.get("models", [])
                    if m["effective_cost_per_1k_tokens"] < model["effective_cost_per_1k_tokens"] * 0.7
                ]
                
                if cheaper_alternatives:
                    # Sort by cost per token (ascending)
                    cheaper_alternatives.sort(key=lambda m: m["effective_cost_per_1k_tokens"])
                    best_alternative = cheaper_alternatives[0]
                    
                    potential_savings = model["total_cost"] - (model["total_tokens"] / 1000 * best_alternative["effective_cost_per_1k_tokens"])
                    
                    recommendations.append({
                        "type": "model_substitution",
                        "current_model": f"{model['provider']}:{model['model_id']}",
                        "recommended_model": f"{best_alternative['provider']}:{best_alternative['model_id']}",
                        "current_cost_per_1k_tokens": model["effective_cost_per_1k_tokens"],
                        "recommended_cost_per_1k_tokens": best_alternative["effective_cost_per_1k_tokens"],
                        "monthly_token_volume": model["total_tokens"],
                        "potential_monthly_savings": potential_savings,
                        "savings_percentage": (potential_savings / model["total_cost"] * 100) if model["total_cost"] > 0 else 0
                    })
        
        # Check for high token usage
        if api_costs.get("total_tokens", 0) > 1000000:
            recommendations.append({
                "type": "token_optimization",
                "current_monthly_tokens": api_costs.get("total_tokens", 0),
                "current_monthly_cost": api_costs.get("total_cost", 0),
                "suggestion": "Implement caching for common queries to reduce token usage",
                "estimated_savings_percentage": 15,
                "potential_monthly_savings": api_costs.get("total_cost", 0) * 0.15
            })
        
        # Get cost summary by user
        user_costs = self.get_cost_summary(
            start_time=datetime.utcnow() - timedelta(days=30),
            group_by="user_id"
        )
        
        # Check for users with high costs
        high_cost_users = [
            g for g in user_costs.get("groups", [])
            if g["percentage"] > 20 and g["key"] != "anonymous"
        ]
        
        if high_cost_users:
            for user in high_cost_users:
                recommendations.append({
                    "type": "user_quota",
                    "user_id": user["key"],
                    "monthly_cost": user["total_cost"],
                    "percentage_of_total": user["percentage"],
                    "suggestion": "Consider implementing usage quotas for high-volume users",
                    "estimated_savings_percentage": 10,
                    "potential_monthly_savings": user["total_cost"] * 0.1
                })
        
        return recommendations


class BusinessImpactAnalytics:
    """
    Analyzes business impact metrics and correlations.
    """
    
    def __init__(self, event_collector: EventCollector):
        """
        Initialize the business impact analytics.
        
        Args:
            event_collector: Event collector to use for tracking events
        """
        self.event_collector = event_collector
        logger.info("Initialized BusinessImpactAnalytics")
    
    def track_business_metric(self, metric_name: str, value: float,
                            category: str, user_id: Optional[str] = None,
                            properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a business metric event.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            category: Metric category
            user_id: Optional user identifier
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties.update({
            "metric_name": metric_name,
            "value": value,
            "category": category
        })
        
        self.event_collector.track_event("business_metric", user_id, event_properties)
    
    def track_conversion(self, conversion_type: str, value: float = 1.0,
                       user_id: Optional[str] = None,
                       properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a conversion event.
        
        Args:
            conversion_type: Type of conversion
            value: Conversion value
            user_id: Optional user identifier
            properties: Optional additional properties
        """
        event_properties = properties or {}
        event_properties.update({
            "conversion_type": conversion_type,
            "value": value
        })
        
        self.event_collector.track_event("conversion", user_id, event_properties)
    
    def get_business_metrics(self, metric_name: Optional[str] = None,
                           category: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           interval_days: int = 1) -> Dict[str, Any]:
        """
        Get business metrics over time.
        
        Args:
            metric_name: Optional metric name to filter by
            category: Optional category to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            interval_days: Time interval for aggregation in days
            
        Returns:
            Business metrics over time
        """
        # Get business metric events
        events = self.event_collector.get_events(
            event_type="business_metric",
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        # Apply filters
        if metric_name:
            events = [e for e in events if e["properties"].get("metric_name") == metric_name]
        
        if category:
            events = [e for e in events if e["properties"].get("category") == category]
        
        if not events:
            return {"metrics": []}
        
        # Determine time range
        if start_time is None:
            start_time = datetime.fromisoformat(min(e["timestamp"] for e in events).split("+")[0])
        
        if end_time is None:
            end_time = datetime.fromisoformat(max(e["timestamp"] for e in events).split("+")[0])
        
        # Create time intervals
        interval_delta = timedelta(days=interval_days)
        intervals = []
        
        current_time = start_time
        while current_time <= end_time:
            intervals.append({
                "start": current_time,
                "end": current_time + interval_delta,
                "data": {}
            })
            current_time += interval_delta
        
        # Group by metric name and category
        metrics = {}
        for event in events:
            name = event["properties"].get("metric_name", "unknown")
            cat = event["properties"].get("category", "unknown")
            key = f"{cat}:{name}"
            
            if key not in metrics:
                metrics[key] = {
                    "metric_name": name,
                    "category": cat,
                    "intervals": []
                }
        
        # Populate intervals for each metric
        for key, metric in metrics.items():
            # Initialize intervals
            metric["intervals"] = [
                {
                    "start_time": interval["start"].isoformat(),
                    "end_time": interval["end"].isoformat(),
                    "values": []
                }
                for interval in intervals
            ]
            
            # Add data points to intervals
            for event in events:
                if (event["properties"].get("metric_name") == metric["metric_name"] and
                    event["properties"].get("category") == metric["category"]):
                    
                    event_time = datetime.fromisoformat(event["timestamp"].split("+")[0])
                    value = event["properties"].get("value", 0)
                    
                    # Find the right interval
                    for i, interval in enumerate(intervals):
                        if interval["start"] <= event_time < interval["end"]:
                            metric["intervals"][i]["values"].append(value)
                            break
            
            # Calculate statistics for each interval
            for interval in metric["intervals"]:
                values = interval["values"]
                if values:
                    interval["sum"] = sum(values)
                    interval["avg"] = sum(values) / len(values)
                    interval["min"] = min(values)
                    interval["max"] = max(values)
                    interval["count"] = len(values)
                else:
                    interval["sum"] = 0
                    interval["avg"] = 0
                    interval["min"] = 0
                    interval["max"] = 0
                    interval["count"] = 0
                
                del interval["values"]  # Remove raw values from result
        
        return {"metrics": list(metrics.values())}
    
    def get_conversion_rates(self, conversion_type: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get conversion rates.
        
        Args:
            conversion_type: Optional conversion type to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            Conversion rate statistics
        """
        # Get conversion events
        events = self.event_collector.get_events(
            event_type="conversion",
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        # Filter by conversion type
        if conversion_type:
            events = [e for e in events if e["properties"].get("conversion_type") == conversion_type]
        
        if not events:
            return {"total_conversions": 0, "conversion_types": []}
        
        # Get user session events for the same time period
        session_events = self.event_collector.get_events(
            event_type="user_session",
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        # Count unique sessions
        unique_sessions = set()
        for event in session_events:
            if event["properties"].get("session_start", False):
                session_id = event["properties"].get("session_id")
                if session_id:
                    unique_sessions.add(session_id)
        
        total_sessions = len(unique_sessions)
        
        # Group by conversion type
        conversion_types = {}
        for event in events:
            conv_type = event["properties"].get("conversion_type", "unknown")
            value = event["properties"].get("value", 1.0)
            
            if conv_type not in conversion_types:
                conversion_types[conv_type] = {
                    "conversion_type": conv_type,
                    "count": 0,
                    "total_value": 0,
                    "unique_users": set()
                }
            
            conversion_types[conv_type]["count"] += 1
            conversion_types[conv_type]["total_value"] += value
            
            if event["user_id"]:
                conversion_types[conv_type]["unique_users"].add(event["user_id"])
        
        # Calculate statistics for each conversion type
        for conv_data in conversion_types.values():
            conv_data["unique_users"] = len(conv_data["unique_users"])
            conv_data["avg_value"] = conv_data["total_value"] / conv_data["count"] if conv_data["count"] > 0 else 0
            
            # Calculate conversion rate if we have session data
            if total_sessions > 0:
                conv_data["conversion_rate"] = conv_data["count"] / total_sessions
            else:
                conv_data["conversion_rate"] = 0
        
        # Prepare results
        results = {
            "total_conversions": sum(c["count"] for c in conversion_types.values()),
            "total_sessions": total_sessions,
            "overall_conversion_rate": sum(c["count"] for c in conversion_types.values()) / total_sessions if total_sessions > 0 else 0,
            "conversion_types": list(conversion_types.values())
        }
        
        # Sort conversion types by count (descending)
        results["conversion_types"].sort(key=lambda c: c["count"], reverse=True)
        
        return results
    
    def correlate_metrics(self, metric1: str, metric2: str,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Correlate two business metrics.
        
        Args:
            metric1: First metric name
            metric2: Second metric name
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            Correlation analysis
        """
        # Get business metric events
        events = self.event_collector.get_events(
            event_type="business_metric",
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        # Filter to relevant metrics
        metric1_events = [e for e in events if e["properties"].get("metric_name") == metric1]
        metric2_events = [e for e in events if e["properties"].get("metric_name") == metric2]
        
        if not metric1_events or not metric2_events:
            return {
                "metric1": metric1,
                "metric2": metric2,
                "correlation": 0,
                "error": "Insufficient data for correlation analysis"
            }
        
        # Group events by day
        metric1_by_day = {}
        metric2_by_day = {}
        
        for event in metric1_events:
            day = event["timestamp"].split("T")[0]
            value = event["properties"].get("value", 0)
            
            if day not in metric1_by_day:
                metric1_by_day[day] = []
            
            metric1_by_day[day].append(value)
        
        for event in metric2_events:
            day = event["timestamp"].split("T")[0]
            value = event["properties"].get("value", 0)
            
            if day not in metric2_by_day:
                metric2_by_day[day] = []
            
            metric2_by_day[day].append(value)
        
        # Calculate daily averages
        metric1_daily_avg = {day: sum(values) / len(values) for day, values in metric1_by_day.items()}
        metric2_daily_avg = {day: sum(values) / len(values) for day, values in metric2_by_day.items()}
        
        # Find common days
        common_days = set(metric1_daily_avg.keys()) & set(metric2_daily_avg.keys())
        
        if len(common_days) < 5:
            return {
                "metric1": metric1,
                "metric2": metric2,
                "correlation": 0,
                "error": "Insufficient overlapping data points for correlation analysis"
            }
        
        # Extract paired values
        paired_values = [
            (metric1_daily_avg[day], metric2_daily_avg[day])
            for day in common_days
        ]
        
        # Calculate correlation coefficient
        try:
            import numpy as np
            
            x = np.array([p[0] for p in paired_values])
            y = np.array([p[1] for p in paired_values])
            
            correlation = np.corrcoef(x, y)[0, 1]
            
            # Prepare data points for visualization
            data_points = [
                {"date": day, "metric1": metric1_daily_avg[day], "metric2": metric2_daily_avg[day]}
                for day in sorted(common_days)
            ]
            
            return {
                "metric1": metric1,
                "metric2": metric2,
                "correlation": correlation,
                "data_points": data_points,
                "interpretation": self._interpret_correlation(correlation)
            }
        except ImportError:
            # Fallback if numpy is not available
            return {
                "metric1": metric1,
                "metric2": metric2,
                "correlation": 0,
                "error": "Correlation analysis requires numpy library"
            }
    
    def _interpret_correlation(self, correlation: float) -> str:
        """
        Interpret a correlation coefficient.
        
        Args:
            correlation: Correlation coefficient
            
        Returns:
            Interpretation string
        """
        abs_corr = abs(correlation)
        
        if abs_corr < 0.1:
            strength = "No"
        elif abs_corr < 0.3:
            strength = "Weak"
        elif abs_corr < 0.5:
            strength = "Moderate"
        elif abs_corr < 0.7:
            strength = "Strong"
        else:
            strength = "Very strong"
        
        direction = "positive" if correlation >= 0 else "negative"
        
        return f"{strength} {direction} correlation"


class AnalyticsSystem:
    """
    Main class that integrates all analytics components.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize the analytics system.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        
        # Initialize components
        self.event_collector = EventCollector(service_name)
        self.user_analytics = UserAnalytics(self.event_collector)
        self.performance_analytics = PerformanceAnalytics(self.event_collector)
        self.cost_analytics = CostAnalytics(self.event_collector)
        self.business_analytics = BusinessImpactAnalytics(self.event_collector)
        
        logger.info(f"Initialized AnalyticsSystem for service {service_name}")
    
    def track_event(self, event_type: str, user_id: Optional[str] = None, 
                   properties: Optional[Dict[str, Any]] = None) -> str:
        """
        Track a generic analytics event.
        
        Args:
            event_type: Type of event
            user_id: Optional user identifier
            properties: Optional event properties
            
        Returns:
            Unique event ID
        """
        return self.event_collector.track_event(event_type, user_id, properties)
    
    def generate_insights(self) -> Dict[str, Any]:
        """
        Generate comprehensive insights from analytics data.
        
        Returns:
            Dictionary containing insights
        """
        insights = {
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "user_insights": [],
            "performance_insights": [],
            "cost_insights": [],
            "business_insights": []
        }
        
        # Time ranges
        now = datetime.utcnow()
        last_day = now - timedelta(days=1)
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        
        # User insights
        try:
            # Feature usage analysis
            feature_usage = self.user_analytics.get_feature_usage(start_time=last_month)
            
            if feature_usage["total_usage"] > 0:
                # Most popular features
                popular_features = feature_usage["features"][:3]
                
                insights["user_insights"].append({
                    "type": "popular_features",
                    "features": [f["feature_id"] for f in popular_features],
                    "usage_counts": [f["usage_count"] for f in popular_features],
                    "insight": f"The most popular features are {', '.join(f['feature_id'] for f in popular_features)}"
                })
                
                # Unused features
                if len(feature_usage["features"]) > 5:
                    unused_features = feature_usage["features"][-3:]
                    if unused_features[-1]["usage_count"] < feature_usage["features"][0]["usage_count"] * 0.1:
                        insights["user_insights"].append({
                            "type": "unused_features",
                            "features": [f["feature_id"] for f in unused_features],
                            "usage_counts": [f["usage_count"] for f in unused_features],
                            "insight": f"Features with low usage: {', '.join(f['feature_id'] for f in unused_features)}"
                        })
        except Exception as e:
            logger.error(f"Error generating user insights: {str(e)}")
        
        # Performance insights
        try:
            # API performance analysis
            api_perf = self.performance_analytics.get_api_performance(start_time=last_week)
            
            if api_perf["total_requests"] > 0:
                # Slow endpoints
                slow_endpoints = [e for e in api_perf["endpoints"] if e["avg_duration_ms"] > 500]
                if slow_endpoints:
                    insights["performance_insights"].append({
                        "type": "slow_endpoints",
                        "endpoints": [e["endpoint"] for e in slow_endpoints],
                        "avg_durations": [e["avg_duration_ms"] for e in slow_endpoints],
                        "insight": f"Slow endpoints with avg response time >500ms: {', '.join(e['endpoint'] for e in slow_endpoints)}"
                    })
                
                # High error rate endpoints
                error_endpoints = [e for e in api_perf["endpoints"] if e["error_rate"] > 0.05 and e["total_requests"] > 10]
                if error_endpoints:
                    insights["performance_insights"].append({
                        "type": "error_endpoints",
                        "endpoints": [e["endpoint"] for e in error_endpoints],
                        "error_rates": [e["error_rate"] for e in error_endpoints],
                        "insight": f"Endpoints with high error rates: {', '.join(e['endpoint'] for e in error_endpoints)}"
                    })
            
            # Model performance analysis
            model_perf = self.performance_analytics.get_model_performance(start_time=last_week)
            
            if model_perf["total_inferences"] > 0:
                # Fastest models
                models = model_perf["models"]
                if len(models) > 1:
                    # Sort by avg duration (ascending)
                    sorted_models = sorted(models, key=lambda m: m["avg_duration_ms"])
                    fastest = sorted_models[0]
                    slowest = sorted_models[-1]
                    
                    if fastest["avg_duration_ms"] < slowest["avg_duration_ms"] * 0.5:
                        insights["performance_insights"].append({
                            "type": "model_performance_comparison",
                            "fastest_model": f"{fastest['provider']}:{fastest['model_id']}",
                            "fastest_duration": fastest["avg_duration_ms"],
                            "slowest_model": f"{slowest['provider']}:{slowest['model_id']}",
                            "slowest_duration": slowest["avg_duration_ms"],
                            "insight": f"{fastest['provider']}:{fastest['model_id']} is {slowest['avg_duration_ms']/fastest['avg_duration_ms']:.1f}x faster than {slowest['provider']}:{slowest['model_id']}"
                        })
        except Exception as e:
            logger.error(f"Error generating performance insights: {str(e)}")
        
        # Cost insights
        try:
            # Cost optimization recommendations
            cost_recommendations = self.cost_analytics.get_cost_optimization_recommendations()
            
            if cost_recommendations:
                total_potential_savings = sum(r.get("potential_monthly_savings", 0) for r in cost_recommendations)
                
                insights["cost_insights"].append({
                    "type": "cost_optimization",
                    "recommendation_count": len(cost_recommendations),
                    "potential_monthly_savings": total_potential_savings,
                    "recommendations": cost_recommendations,
                    "insight": f"Identified {len(cost_recommendations)} cost optimization opportunities with potential monthly savings of ${total_potential_savings:.2f}"
                })
            
            # API cost analysis
            api_costs = self.cost_analytics.get_api_cost_analysis(start_time=last_month)
            
            if api_costs["total_cost"] > 0:
                # Most expensive models
                expensive_models = api_costs["models"][:3]
                
                insights["cost_insights"].append({
                    "type": "expensive_models",
                    "models": [f"{m['provider']}:{m['model_id']}" for m in expensive_models],
                    "costs": [m["total_cost"] for m in expensive_models],
                    "percentages": [m["percentage"] for m in expensive_models],
                    "insight": f"Top 3 models by cost: {', '.join(f'{m['provider']}:{m['model_id']} (${m['total_cost']:.2f}, {m['percentage']:.1f}%)' for m in expensive_models)}"
                })
        except Exception as e:
            logger.error(f"Error generating cost insights: {str(e)}")
        
        # Business insights
        try:
            # Conversion rates
            conversion_rates = self.business_analytics.get_conversion_rates(start_time=last_month)
            
            if conversion_rates["total_conversions"] > 0:
                insights["business_insights"].append({
                    "type": "conversion_rates",
                    "overall_rate": conversion_rates["overall_conversion_rate"],
                    "total_conversions": conversion_rates["total_conversions"],
                    "total_sessions": conversion_rates["total_sessions"],
                    "conversion_types": [c["conversion_type"] for c in conversion_rates["conversion_types"]],
                    "rates": [c["conversion_rate"] for c in conversion_rates["conversion_types"]],
                    "insight": f"Overall conversion rate: {conversion_rates['overall_conversion_rate']*100:.1f}% ({conversion_rates['total_conversions']} conversions from {conversion_rates['total_sessions']} sessions)"
                })
        except Exception as e:
            logger.error(f"Error generating business insights: {str(e)}")
        
        return insights


# Example usage
if __name__ == "__main__":
    # Initialize analytics system
    analytics = AnalyticsSystem("example-service")
    
    # Track some example events
    user_id = "user-123"
    session_id = "session-456"
    
    # Track user session
    analytics.user_analytics.track_user_session(
        user_id=user_id,
        session_id=session_id,
        session_start=True,
        properties={"source": "web", "browser": "chrome"}
    )
    
    # Track feature usage
    analytics.user_analytics.track_feature_usage(
        user_id=user_id,
        feature_id="search",
        session_id=session_id,
        properties={"query": "example search"}
    )
    
    analytics.user_analytics.track_feature_usage(
        user_id=user_id,
        feature_id="chat",
        session_id=session_id,
        properties={"message_count": 3}
    )
    
    # Track API request
    analytics.performance_analytics.track_api_request(
        endpoint="/api/search",
        method="GET",
        status_code=200,
        duration_ms=150,
        user_id=user_id,
        properties={"query_params": {"q": "example"}}
    )
    
    # Track model inference
    analytics.performance_analytics.track_model_inference(
        model_id="gpt-4",
        provider="openai",
        duration_ms=2500,
        token_count=150,
        success=True,
        user_id=user_id
    )
    
    # Track API cost
    analytics.cost_analytics.track_api_cost(
        provider="openai",
        model_id="gpt-4",
        token_count=150,
        cost_per_1k_tokens=0.06,
        user_id=user_id
    )
    
    # Track business metric
    analytics.business_analytics.track_business_metric(
        metric_name="search_count",
        value=1,
        category="usage",
        user_id=user_id
    )
    
    # Track conversion
    analytics.business_analytics.track_conversion(
        conversion_type="signup",
        value=1.0,
        user_id=user_id
    )
    
    # End user session
    analytics.user_analytics.track_user_session(
        user_id=user_id,
        session_id=session_id,
        session_end=True,
        duration_seconds=300,
        properties={"pages_visited": 5}
    )
    
    # Generate insights
    insights = analytics.generate_insights()
    print(json.dumps(insights, indent=2))
