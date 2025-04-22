"""
Tool Monitoring module for Lumina AI's Expanded Tool Ecosystem.

This module provides functionality for monitoring tool executions, collecting metrics,
and generating insights about tool usage and performance.
"""

import time
import datetime
import threading
import statistics
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import json

from .registry import ToolRegistry
from .execution import ToolExecutionEngine, ToolExecutionResult, ToolExecutionStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolMetric:
    """Represents a metric collected for tool executions."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize tool metric.
        
        Args:
            name: Metric name
            description: Metric description
        """
        self.name = name
        self.description = description
        self.values: List[float] = []
        self.timestamps: List[datetime.datetime] = []
    
    def add_value(self, value: float) -> None:
        """
        Add a new metric value.
        
        Args:
            value: Metric value
        """
        self.values.append(value)
        self.timestamps.append(datetime.datetime.now())
    
    def get_average(self) -> Optional[float]:
        """
        Get average metric value.
        
        Returns:
            Average value or None if no values
        """
        if not self.values:
            return None
        return sum(self.values) / len(self.values)
    
    def get_min(self) -> Optional[float]:
        """
        Get minimum metric value.
        
        Returns:
            Minimum value or None if no values
        """
        if not self.values:
            return None
        return min(self.values)
    
    def get_max(self) -> Optional[float]:
        """
        Get maximum metric value.
        
        Returns:
            Maximum value or None if no values
        """
        if not self.values:
            return None
        return max(self.values)
    
    def get_median(self) -> Optional[float]:
        """
        Get median metric value.
        
        Returns:
            Median value or None if no values
        """
        if not self.values:
            return None
        return statistics.median(self.values)
    
    def get_percentile(self, percentile: float) -> Optional[float]:
        """
        Get percentile metric value.
        
        Args:
            percentile: Percentile (0-100)
            
        Returns:
            Percentile value or None if no values
        """
        if not self.values:
            return None
        return statistics.quantiles(self.values, n=100)[int(percentile) - 1]
    
    def get_recent_values(self, count: int) -> List[Tuple[datetime.datetime, float]]:
        """
        Get most recent metric values with timestamps.
        
        Args:
            count: Number of values to return
            
        Returns:
            List of (timestamp, value) tuples
        """
        if not self.values:
            return []
        
        recent = list(zip(self.timestamps, self.values))
        recent.sort(reverse=True)
        return recent[:count]
    
    def clear(self) -> None:
        """Clear all metric values."""
        self.values = []
        self.timestamps = []


class ToolMonitoring:
    """
    Service for monitoring tool executions and collecting metrics.
    
    Provides functionality for:
    - Tracking execution success/failure rates
    - Measuring execution times
    - Collecting usage statistics
    - Generating performance insights
    """
    
    def __init__(self, registry: ToolRegistry, engine: ToolExecutionEngine):
        """
        Initialize tool monitoring service.
        
        Args:
            registry: Tool registry
            engine: Tool execution engine
        """
        self.registry = registry
        self.engine = engine
        self.metrics: Dict[str, Dict[str, ToolMetric]] = {}  # tool_id -> metric_name -> metric
        self.global_metrics: Dict[str, ToolMetric] = {}
        self.execution_history: Dict[str, List[ToolExecutionResult]] = {}  # tool_id -> list of results
        self.max_history_per_tool = 100
        
        # Initialize standard metrics
        self._init_standard_metrics()
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _init_standard_metrics(self) -> None:
        """Initialize standard metrics for all tools."""
        # Global metrics
        self.global_metrics["total_executions"] = ToolMetric(
            name="total_executions",
            description="Total number of tool executions"
        )
        self.global_metrics["success_rate"] = ToolMetric(
            name="success_rate",
            description="Overall success rate of tool executions"
        )
        self.global_metrics["average_execution_time"] = ToolMetric(
            name="average_execution_time",
            description="Average execution time across all tools"
        )
        
        # Per-tool metrics
        for tool_id in self.registry.tools:
            self._init_tool_metrics(tool_id)
    
    def _init_tool_metrics(self, tool_id: str) -> None:
        """
        Initialize metrics for a specific tool.
        
        Args:
            tool_id: Tool ID
        """
        if tool_id not in self.metrics:
            self.metrics[tool_id] = {}
            self.execution_history[tool_id] = []
        
        tool_metrics = self.metrics[tool_id]
        
        # Standard metrics
        tool_metrics["execution_count"] = ToolMetric(
            name="execution_count",
            description="Number of executions"
        )
        tool_metrics["success_count"] = ToolMetric(
            name="success_count",
            description="Number of successful executions"
        )
        tool_metrics["failure_count"] = ToolMetric(
            name="failure_count",
            description="Number of failed executions"
        )
        tool_metrics["timeout_count"] = ToolMetric(
            name="timeout_count",
            description="Number of timed out executions"
        )
        tool_metrics["execution_time"] = ToolMetric(
            name="execution_time",
            description="Execution time in seconds"
        )
        tool_metrics["success_rate"] = ToolMetric(
            name="success_rate",
            description="Success rate (percentage)"
        )
    
    def _monitor_loop(self) -> None:
        """Background thread for monitoring executions."""
        while self.running:
            try:
                # Check for new tools
                for tool_id in self.registry.tools:
                    if tool_id not in self.metrics:
                        self._init_tool_metrics(tool_id)
                
                # Sleep for a bit
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def record_execution(self, result: ToolExecutionResult) -> None:
        """
        Record a tool execution result.
        
        Args:
            result: Tool execution result
        """
        tool_id = result.tool_id
        
        # Initialize metrics if needed
        if tool_id not in self.metrics:
            self._init_tool_metrics(tool_id)
        
        # Get tool metrics
        tool_metrics = self.metrics[tool_id]
        
        # Update execution count
        tool_metrics["execution_count"].add_value(1)
        self.global_metrics["total_executions"].add_value(1)
        
        # Update success/failure counts
        if result.status == ToolExecutionStatus.COMPLETED:
            tool_metrics["success_count"].add_value(1)
        elif result.status == ToolExecutionStatus.FAILED:
            tool_metrics["failure_count"].add_value(1)
        elif result.status == ToolExecutionStatus.TIMEOUT:
            tool_metrics["timeout_count"].add_value(1)
        
        # Update execution time
        if result.execution_time is not None:
            tool_metrics["execution_time"].add_value(result.execution_time)
            self.global_metrics["average_execution_time"].add_value(result.execution_time)
        
        # Update success rate
        success_count = tool_metrics["success_count"].get_average() or 0
        total_count = tool_metrics["execution_count"].get_average() or 1
        success_rate = (success_count / total_count) * 100
        tool_metrics["success_rate"].add_value(success_rate)
        
        # Update global success rate
        total_executions = self.global_metrics["total_executions"].get_average() or 0
        total_successes = sum(
            self.metrics[t_id]["success_count"].get_average() or 0
            for t_id in self.metrics
        )
        global_success_rate = (total_successes / total_executions) * 100 if total_executions > 0 else 0
        self.global_metrics["success_rate"].add_value(global_success_rate)
        
        # Add to execution history
        history = self.execution_history[tool_id]
        history.append(result)
        
        # Trim history if needed
        if len(history) > self.max_history_per_tool:
            history.pop(0)
    
    def add_custom_metric(self, tool_id: str, metric_name: str, description: str) -> None:
        """
        Add a custom metric for a tool.
        
        Args:
            tool_id: Tool ID
            metric_name: Metric name
            description: Metric description
        """
        if tool_id not in self.registry.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        if tool_id not in self.metrics:
            self._init_tool_metrics(tool_id)
        
        if metric_name in self.metrics[tool_id]:
            raise ValueError(f"Metric '{metric_name}' already exists for tool {tool_id}")
        
        self.metrics[tool_id][metric_name] = ToolMetric(
            name=metric_name,
            description=description
        )
        
        logger.info(f"Added custom metric '{metric_name}' for tool {self.registry.get_tool(tool_id).name}")
    
    def add_custom_global_metric(self, metric_name: str, description: str) -> None:
        """
        Add a custom global metric.
        
        Args:
            metric_name: Metric name
            description: Metric description
        """
        if metric_name in self.global_metrics:
            raise ValueError(f"Global metric '{metric_name}' already exists")
        
        self.global_metrics[metric_name] = ToolMetric(
            name=metric_name,
            description=description
        )
        
        logger.info(f"Added custom global metric '{metric_name}'")
    
    def update_custom_metric(self, tool_id: str, metric_name: str, value: float) -> None:
        """
        Update a custom metric for a tool.
        
        Args:
            tool_id: Tool ID
            metric_name: Metric name
            value: Metric value
        """
        if tool_id not in self.metrics:
            raise ValueError(f"No metrics found for tool {tool_id}")
        
        if metric_name not in self.metrics[tool_id]:
            raise ValueError(f"Metric '{metric_name}' not found for tool {tool_id}")
        
        self.metrics[tool_id][metric_name].add_value(value)
    
    def update_custom_global_metric(self, metric_name: str, value: float) -> None:
        """
        Update a custom global metric.
        
        Args:
            metric_name: Metric name
            value: Metric value
        """
        if metric_name not in self.global_metrics:
            raise ValueError(f"Global metric '{metric_name}' not found")
        
        self.global_metrics[metric_name].add_value(value)
    
    def get_tool_metrics(self, tool_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all metrics for a tool.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Dictionary of metric data
        """
        if tool_id not in self.metrics:
            raise ValueError(f"No metrics found for tool {tool_id}")
        
        result = {}
        
        for metric_name, metric in self.metrics[tool_id].items():
            result[metric_name] = {
                "description": metric.description,
                "average": metric.get_average(),
                "min": metric.get_min(),
                "max": metric.get_max(),
                "median": metric.get_median(),
                "p95": metric.get_percentile(95),
                "recent": metric.get_recent_values(5)
            }
        
        return result
    
    def get_global_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all global metrics.
        
        Returns:
            Dictionary of metric data
        """
        result = {}
        
        for metric_name, metric in self.global_metrics.items():
            result[metric_name] = {
                "description": metric.description,
                "average": metric.get_average(),
                "min": metric.get_min(),
                "max": metric.get_max(),
                "median": metric.get_median(),
                "p95": metric.get_percentile(95),
                "recent": metric.get_recent_values(5)
            }
        
        return result
    
    def get_tool_execution_history(self, tool_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get execution history for a tool.
        
        Args:
            tool_id: Tool ID
            limit: Maximum number of results to return
            
        Returns:
            List of execution results
        """
        if tool_id not in self.execution_history:
            raise ValueError(f"No execution history found for tool {tool_id}")
        
        history = self.execution_history[tool_id]
        return [result.to_dict() for result in history[-limit:]]
    
    def get_performance_insights(self, tool_id: str) -> Dict[str, Any]:
        """
        Generate performance insights for a tool.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Dictionary of insights
        """
        if tool_id not in self.metrics:
            raise ValueError(f"No metrics found for tool {tool_id}")
        
        tool_metrics = self.metrics[tool_id]
        
        # Get key metrics
        execution_count = tool_metrics["execution_count"].get_average() or 0
        success_rate = tool_metrics["success_rate"].get_average() or 0
        avg_execution_time = tool_metrics["execution_time"].get_average() or 0
        p95_execution_time = tool_metrics["execution_time"].get_percentile(95) or 0
        
        # Generate insights
        insights = {
            "summary": {
                "execution_count": execution_count,
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "p95_execution_time": p95_execution_time
            },
            "performance_rating": self._calculate_performance_rating(tool_id),
            "issues": self._identify_issues(tool_id),
            "recommendations": self._generate_recommendations(tool_id)
        }
        
        return insights
    
    def _calculate_performance_rating(self, tool_id: str) -> str:
        """
        Calculate performance rating for a tool.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Performance rating (Excellent, Good, Fair, Poor)
        """
        tool_metrics = self.metrics[tool_id]
        
        success_rate = tool_metrics["success_rate"].get_average() or 0
        execution_time = tool_metrics["execution_time"].get_average() or 0
        
        # Simple rating algorithm
        if success_rate >= 95 and execution_time < 1.0:
            return "Excellent"
        elif success_rate >= 90 and execution_time < 2.0:
            return "Good"
        elif success_rate >= 80 and execution_time < 5.0:
            return "Fair"
        else:
            return "Poor"
    
    def _identify_issues(self, tool_id: str) -> List[str]:
        """
        Identify potential issues with a tool.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            List of issue descriptions
        """
        tool_metrics = self.metrics[tool_id]
        issues = []
        
        # Check success rate
        success_rate = tool_metrics["success_rate"].get_average() or 0
        if success_rate < 80:
            issues.append(f"Low success rate ({success_rate:.1f}%)")
        
        # Check execution time
        avg_time = tool_metrics["execution_time"].get_average() or 0
        p95_time = tool_metrics["execution_time"].get_percentile(95) or 0
        
        if avg_time > 5.0:
            issues.append(f"High average execution time ({avg_time:.2f}s)")
        
        if p95_time > 10.0:
            issues.append(f"High p95 execution time ({p95_time:.2f}s)")
        
        # Check timeout rate
        timeout_count = tool_metrics["timeout_count"].get_average() or 0
        execution_count = tool_metrics["execution_count"].get_average() or 1
        timeout_rate = (timeout_count / execution_count) * 100
        
        if timeout_rate > 5:
            issues.append(f"High timeout rate ({timeout_rate:.1f}%)")
        
        return issues
    
    def _generate_recommendations(self, tool_id: str) -> List[str]:
        """
        Generate recommendations for improving a tool.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            List of recommendations
        """
        tool_metrics = self.metrics[tool_id]
        issues = self._identify_issues(tool_id)
        recommendations = []
        
        # Generate recommendations based on issues
        for issue in issues:
            if "success rate" in issue.lower():
                recommendations.append("Improve error handling and input validation")
                recommendations.append("Review common failure cases in execution history")
            
            if "execution time" in issue.lower():
                recommendations.append("Optimize performance-critical sections")
                recommendations.append("Consider caching results for repeated operations")
            
            if "timeout" in issue.lower():
                recommendations.append("Increase default timeout value or implement chunking")
                recommendations.append("Optimize long-running operations")
        
        # Add general recommendations if no specific issues
        if not recommendations:
            execution_count = tool_metrics["execution_count"].get_average() or 0
            if execution_count < 10:
                recommendations.append("Increase usage to gather more performance data")
            else:
                recommendations.append("Tool is performing well, no specific recommendations")
        
        return recommendations
    
    def shutdown(self) -> None:
        """Shutdown the monitoring service."""
        self.running = False
        self.monitor_thread.join(timeout=1.0)
        logger.info("Tool monitoring service shut down")
