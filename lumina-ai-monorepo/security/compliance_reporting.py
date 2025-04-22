"""
Lumina AI Security Package - Compliance Reporting Module

This module implements comprehensive compliance reporting for Lumina AI, including:
- Regulatory compliance reporting
- Security policy compliance
- Data protection compliance
- Audit trail reporting
- Compliance dashboard generation

Copyright (c) 2025 AlienNova Technologies. All rights reserved.
"""

import os
import json
import csv
import time
import datetime
import logging
import hashlib
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field

from .audit_logging import AuditLogger, AuditEventFilter, AuditEventType, AuditEventSeverity, AuditEventStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    NIST = "nist"
    PCI_DSS = "pci_dss"
    FEDRAMP = "fedramp"
    CUSTOM = "custom"

class ComplianceRequirement:
    """Represents a compliance requirement."""
    
    def __init__(self, id: str, framework: ComplianceFramework, title: str, description: str, 
                 category: str, severity: str):
        self.id = id
        self.framework = framework
        self.title = title
        self.description = description
        self.category = category
        self.severity = severity
        self.audit_queries: List[Dict[str, Any]] = []
        self.validation_functions: List[Callable[[], Tuple[bool, str]]] = []
    
    def add_audit_query(self, event_type: Optional[AuditEventType] = None, 
                        action: Optional[str] = None,
                        status: Optional[AuditEventStatus] = None,
                        detail_filters: Optional[Dict[str, Any]] = None) -> "ComplianceRequirement":
        """Add an audit query for this requirement."""
        query = {}
        if event_type:
            query["event_type"] = event_type
        if action:
            query["action"] = action
        if status:
            query["status"] = status
        if detail_filters:
            query["detail_filters"] = detail_filters
        
        self.audit_queries.append(query)
        return self
    
    def add_validation_function(self, func: Callable[[], Tuple[bool, str]]) -> "ComplianceRequirement":
        """Add a validation function for this requirement."""
        self.validation_functions.append(func)
        return self

class ComplianceStatus(Enum):
    """Status of compliance with a requirement."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class ComplianceCheckResult:
    """Result of a compliance check."""
    requirement_id: str
    framework: ComplianceFramework
    status: ComplianceStatus
    timestamp: float
    details: str
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    remediation_steps: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "requirement_id": self.requirement_id,
            "framework": self.framework.value,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "details": self.details,
            "evidence": self.evidence,
            "remediation_steps": self.remediation_steps
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplianceCheckResult":
        """Create from dictionary."""
        return cls(
            requirement_id=data["requirement_id"],
            framework=ComplianceFramework(data["framework"]),
            status=ComplianceStatus(data["status"]),
            timestamp=data["timestamp"],
            details=data["details"],
            evidence=data.get("evidence", []),
            remediation_steps=data.get("remediation_steps")
        )

class ComplianceReport:
    """Represents a compliance report."""
    
    def __init__(self, id: str, title: str, description: str, 
                 frameworks: List[ComplianceFramework], generated_at: float):
        self.id = id
        self.title = title
        self.description = description
        self.frameworks = frameworks
        self.generated_at = generated_at
        self.results: List[ComplianceCheckResult] = []
    
    def add_result(self, result: ComplianceCheckResult) -> None:
        """Add a compliance check result to the report."""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the report."""
        total = len(self.results)
        compliant = sum(1 for r in self.results if r.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for r in self.results if r.status == ComplianceStatus.NON_COMPLIANT)
        partially_compliant = sum(1 for r in self.results if r.status == ComplianceStatus.PARTIALLY_COMPLIANT)
        unknown = sum(1 for r in self.results if r.status == ComplianceStatus.UNKNOWN)
        not_applicable = sum(1 for r in self.results if r.status == ComplianceStatus.NOT_APPLICABLE)
        
        compliance_rate = (compliant / total) * 100 if total > 0 else 0
        
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "frameworks": [f.value for f in self.frameworks],
            "generated_at": self.generated_at,
            "total_requirements": total,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "partially_compliant": partially_compliant,
            "unknown": unknown,
            "not_applicable": not_applicable,
            "compliance_rate": compliance_rate
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "frameworks": [f.value for f in self.frameworks],
            "generated_at": self.generated_at,
            "results": [r.to_dict() for r in self.results],
            "summary": self.get_summary()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplianceReport":
        """Create from dictionary."""
        report = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            frameworks=[ComplianceFramework(f) for f in data["frameworks"]],
            generated_at=data["generated_at"]
        )
        
        for result_data in data.get("results", []):
            report.add_result(ComplianceCheckResult.from_dict(result_data))
        
        return report
    
    def export_to_json(self, file_path: str) -> None:
        """Export the report to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def export_to_csv(self, file_path: str) -> None:
        """Export the report to a CSV file."""
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Requirement ID", "Framework", "Status", "Timestamp", 
                "Details", "Remediation Steps"
            ])
            
            # Write results
            for result in self.results:
                timestamp_str = datetime.datetime.fromtimestamp(result.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([
                    result.requirement_id,
                    result.framework.value,
                    result.status.value,
                    timestamp_str,
                    result.details,
                    result.remediation_steps or ""
                ])
    
    def export_to_html(self, file_path: str) -> None:
        """Export the report to an HTML file."""
        summary = self.get_summary()
        
        # Convert timestamp to readable format
        generated_at_str = datetime.datetime.fromtimestamp(self.generated_at).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
                .summary-item {{ margin-bottom: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .compliant {{ color: green; }}
                .non-compliant {{ color: red; }}
                .partially-compliant {{ color: orange; }}
                .unknown {{ color: gray; }}
                .not-applicable {{ color: #999; }}
            </style>
        </head>
        <body>
            <h1>{self.title}</h1>
            <p>{self.description}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="summary-item"><strong>Report ID:</strong> {self.id}</div>
                <div class="summary-item"><strong>Generated At:</strong> {generated_at_str}</div>
                <div class="summary-item"><strong>Frameworks:</strong> {', '.join(summary['frameworks'])}</div>
                <div class="summary-item"><strong>Total Requirements:</strong> {summary['total_requirements']}</div>
                <div class="summary-item"><strong>Compliant:</strong> {summary['compliant']} ({summary['compliance_rate']:.2f}%)</div>
                <div class="summary-item"><strong>Non-Compliant:</strong> {summary['non_compliant']}</div>
                <div class="summary-item"><strong>Partially Compliant:</strong> {summary['partially_compliant']}</div>
                <div class="summary-item"><strong>Unknown:</strong> {summary['unknown']}</div>
                <div class="summary-item"><strong>Not Applicable:</strong> {summary['not_applicable']}</div>
            </div>
            
            <h2>Detailed Results</h2>
            <table>
                <tr>
                    <th>Requirement ID</th>
                    <th>Framework</th>
                    <th>Status</th>
                    <th>Details</th>
                    <th>Remediation Steps</th>
                </tr>
        """
        
        # Add rows for each result
        for result in self.results:
            status_class = result.status.value.replace('_', '-')
            html += f"""
                <tr>
                    <td>{result.requirement_id}</td>
                    <td>{result.framework.value}</td>
                    <td class="{status_class}">{result.status.value}</td>
                    <td>{result.details}</td>
                    <td>{result.remediation_steps or ""}</td>
                </tr>
            """
        
        # Close HTML
        html += """
            </table>
        </body>
        </html>
        """
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write(html)

class ComplianceRegistry:
    """Registry of compliance requirements."""
    
    def __init__(self):
        self.requirements: Dict[str, ComplianceRequirement] = {}
    
    def register_requirement(self, requirement: ComplianceRequirement) -> None:
        """Register a compliance requirement."""
        self.requirements[requirement.id] = requirement
        logger.info(f"Registered compliance requirement: {requirement.id}")
    
    def get_requirement(self, requirement_id: str) -> Optional[ComplianceRequirement]:
        """Get a compliance requirement by ID."""
        return self.requirements.get(requirement_id)
    
    def get_requirements_by_framework(self, framework: ComplianceFramework) -> List[ComplianceRequirement]:
        """Get all requirements for a specific framework."""
        return [r for r in self.requirements.values() if r.framework == framework]
    
    def get_all_requirements(self) -> List[ComplianceRequirement]:
        """Get all registered requirements."""
        return list(self.requirements.values())

class ComplianceChecker:
    """Checks compliance with requirements."""
    
    def __init__(self, registry: ComplianceRegistry, audit_logger: AuditLogger):
        self.registry = registry
        self.audit_logger = audit_logger
    
    def check_requirement(self, requirement_id: str) -> ComplianceCheckResult:
        """Check compliance with a specific requirement."""
        requirement = self.registry.get_requirement(requirement_id)
        if not requirement:
            return ComplianceCheckResult(
                requirement_id=requirement_id,
                framework=ComplianceFramework.CUSTOM,
                status=ComplianceStatus.UNKNOWN,
                timestamp=time.time(),
                details=f"Requirement {requirement_id} not found in registry"
            )
        
        # Check audit queries
        audit_results = []
        for query in requirement.audit_queries:
            filter = AuditEventFilter()
            
            if "event_type" in query:
                filter.add_event_type(query["event_type"])
            
            if "action" in query:
                filter.add_action(query["action"])
            
            if "status" in query:
                filter.add_status(query["status"])
            
            if "detail_filters" in query:
                for key, value in query["detail_filters"].items():
                    filter.add_detail_filter(key, value)
            
            # Set time range to last 30 days
            end_time = time.time()
            start_time = end_time - (30 * 24 * 60 * 60)
            filter.set_time_range(start_time, end_time)
            
            # Query audit events
            events = self.audit_logger.query_events(filter)
            audit_results.append({
                "query": query,
                "events": [e.to_dict() for e in events],
                "count": len(events)
            })
        
        # Run validation functions
        validation_results = []
        for func in requirement.validation_functions:
            try:
                is_compliant, details = func()
                validation_results.append({
                    "is_compliant": is_compliant,
                    "details": details
                })
            except Exception as e:
                validation_results.append({
                    "is_compliant": False,
                    "details": f"Error in validation function: {e}"
                })
        
        # Determine overall compliance status
        if not audit_results and not validation_results:
            status = ComplianceStatus.UNKNOWN
            details = "No audit queries or validation functions defined for this requirement"
        else:
            # Check validation results
            validation_compliant = all(r["is_compliant"] for r in validation_results) if validation_results else True
            
            # Check audit results
            audit_compliant = True
            for result in audit_results:
                # If we're looking for failures and found some, that's non-compliant
                if "status" in result["query"] and result["query"]["status"] == AuditEventStatus.FAILURE and result["count"] > 0:
                    audit_compliant = False
                    break
                
                # If we're looking for successes and found none, that's non-compliant
                if "status" in result["query"] and result["query"]["status"] == AuditEventStatus.SUCCESS and result["count"] == 0:
                    audit_compliant = False
                    break
            
            # Determine overall status
            if validation_compliant and audit_compliant:
                status = ComplianceStatus.COMPLIANT
                details = "All validation checks passed and audit queries indicate compliance"
            elif not validation_compliant and not audit_compliant:
                status = ComplianceStatus.NON_COMPLIANT
                details = "Validation checks failed and audit queries indicate non-compliance"
            else:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
                details = "Some checks passed but others failed"
        
        # Create evidence
        evidence = []
        for i, result in enumerate(audit_results):
            evidence.append({
                "type": "audit_query",
                "index": i,
                "query": result["query"],
                "count": result["count"],
                "sample_events": result["events"][:5]  # Include up to 5 sample events
            })
        
        for i, result in enumerate(validation_results):
            evidence.append({
                "type": "validation",
                "index": i,
                "is_compliant": result["is_compliant"],
                "details": result["details"]
            })
        
        # Generate remediation steps if non-compliant
        remediation_steps = None
        if status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]:
            remediation_steps = f"Review the evidence and address the issues related to {requirement.title}."
        
        # Create and return result
        return ComplianceCheckResult(
            requirement_id=requirement_id,
            framework=requirement.framework,
            status=status,
            timestamp=time.time(),
            details=details,
            evidence=evidence,
            remediation_steps=remediation_steps
        )
    
    def check_framework(self, framework: ComplianceFramework) -> ComplianceReport:
        """Check compliance with all requirements in a framework."""
        requirements = self.registry.get_requirements_by_framework(framework)
        
        # Create report
        report = ComplianceReport(
            id=f"{framework.value}_{int(time.time())}",
            title=f"{framework.value.upper()} Compliance Report",
            description=f"Compliance report for {framework.value.upper()} framework",
            frameworks=[framework],
            generated_at=time.time()
        )
        
        # Check each requirement
        for requirement in requirements:
            result = self.check_requirement(requirement.id)
            report.add_result(result)
        
        return report
    
    def check_all_frameworks(self) -> ComplianceReport:
        """Check compliance with all registered requirements."""
        # Create report
        report = ComplianceReport(
            id=f"all_frameworks_{int(time.time())}",
            title="Comprehensive Compliance Report",
            description="Compliance report for all registered frameworks",
            frameworks=list(set(r.framework for r in self.registry.get_all_requirements())),
            generated_at=time.time()
        )
        
        # Check each requirement
        for requirement in self.registry.get_all_requirements():
            result = self.check_requirement(requirement.id)
            report.add_result(result)
        
        return report

class ComplianceReportStorage:
    """Storage for compliance reports."""
    
    def __init__(self, directory: str):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
    
    def store_report(self, report: ComplianceReport) -> str:
        """Store a compliance report."""
        file_path = os.path.join(self.directory, f"{report.id}.json")
        report.export_to_json(file_path)
        return file_path
    
    def get_report(self, report_id: str) -> Optional[ComplianceReport]:
        """Get a compliance report by ID."""
        file_path = os.path.join(self.directory, f"{report_id}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return ComplianceReport.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load compliance report {report_id}: {e}")
            return None
    
    def list_reports(self) -> List[Dict[str, Any]]:
        """List all stored reports."""
        reports = []
        for filename in os.listdir(self.directory):
            if filename.endswith(".json"):
                report_id = filename[:-5]  # Remove .json extension
                report = self.get_report(report_id)
                if report:
                    reports.append(report.get_summary())
        
        # Sort by generated_at (newest first)
        reports.sort(key=lambda r: r["generated_at"], reverse=True)
        return reports
    
    def export_report(self, report_id: str, format: str, output_path: Optional[str] = None) -> Optional[str]:
        """Export a report in the specified format."""
        report = self.get_report(report_id)
        if not report:
            return None
        
        if not output_path:
            output_path = os.path.join(self.directory, f"{report_id}.{format}")
        
        if format.lower() == "json":
            report.export_to_json(output_path)
        elif format.lower() == "csv":
            report.export_to_csv(output_path)
        elif format.lower() == "html":
            report.export_to_html(output_path)
        else:
            logger.error(f"Unsupported export format: {format}")
            return None
        
        return output_path

class ComplianceScheduler:
    """Schedules regular compliance checks."""
    
    def __init__(self, checker: ComplianceChecker, storage: ComplianceReportStorage):
        self.checker = checker
        self.storage = storage
        self.schedules = {}
    
    def schedule_check(self, name: str, framework: Optional[ComplianceFramework] = None, 
                      interval_days: int = 30, next_run: Optional[float] = None) -> None:
        """Schedule a regular compliance check."""
        if next_run is None:
            next_run = time.time()
        
        self.schedules[name] = {
            "framework": framework,
            "interval_days": interval_days,
            "next_run": next_run,
            "last_report_id": None
        }
        
        logger.info(f"Scheduled compliance check '{name}' with interval {interval_days} days")
    
    def run_due_checks(self) -> List[str]:
        """Run all due compliance checks."""
        now = time.time()
        report_ids = []
        
        for name, schedule in self.schedules.items():
            if schedule["next_run"] <= now:
                logger.info(f"Running scheduled compliance check: {name}")
                
                # Run check
                if schedule["framework"] is None:
                    report = self.checker.check_all_frameworks()
                else:
                    report = self.checker.check_framework(schedule["framework"])
                
                # Store report
                self.storage.store_report(report)
                report_ids.append(report.id)
                
                # Update schedule
                self.schedules[name]["last_report_id"] = report.id
                self.schedules[name]["next_run"] = now + (schedule["interval_days"] * 24 * 60 * 60)
                
                logger.info(f"Completed scheduled compliance check: {name}, next run at {self.schedules[name]['next_run']}")
        
        return report_ids
    
    def get_schedule(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a schedule by name."""
        return self.schedules.get(name)
    
    def get_all_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Get all schedules."""
        return self.schedules
    
    def remove_schedule(self, name: str) -> bool:
        """Remove a schedule."""
        if name in self.schedules:
            del self.schedules[name]
            logger.info(f"Removed compliance check schedule: {name}")
            return True
        return False

# Initialize default GDPR requirements
def initialize_gdpr_requirements(registry: ComplianceRegistry) -> None:
    """Initialize default GDPR compliance requirements."""
    # Data Protection by Design and Default
    req = ComplianceRequirement(
        id="gdpr-art25-1",
        framework=ComplianceFramework.GDPR,
        title="Data Protection by Design and Default",
        description="Implement appropriate technical and organizational measures for ensuring that, by default, only personal data which are necessary for each specific purpose of the processing are processed.",
        category="Privacy",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.PRIVACY_EVENT,
        action="data_minimization_check",
        status=AuditEventStatus.SUCCESS
    )
    registry.register_requirement(req)
    
    # Records of Processing Activities
    req = ComplianceRequirement(
        id="gdpr-art30-1",
        framework=ComplianceFramework.GDPR,
        title="Records of Processing Activities",
        description="Maintain a record of processing activities under your responsibility.",
        category="Documentation",
        severity="Medium"
    )
    req.add_audit_query(
        event_type=AuditEventType.COMPLIANCE_EVENT,
        action="processing_records_check",
        status=AuditEventStatus.SUCCESS
    )
    registry.register_requirement(req)
    
    # Security of Processing
    req = ComplianceRequirement(
        id="gdpr-art32-1",
        framework=ComplianceFramework.GDPR,
        title="Security of Processing",
        description="Implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk.",
        category="Security",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.SECURITY_ALERT,
        status=AuditEventStatus.FAILURE
    )
    registry.register_requirement(req)
    
    # Data Protection Impact Assessment
    req = ComplianceRequirement(
        id="gdpr-art35-1",
        framework=ComplianceFramework.GDPR,
        title="Data Protection Impact Assessment",
        description="Carry out an assessment of the impact of the envisaged processing operations on the protection of personal data where processing is likely to result in a high risk.",
        category="Risk Assessment",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.COMPLIANCE_EVENT,
        action="dpia_check",
        status=AuditEventStatus.SUCCESS
    )
    registry.register_requirement(req)

# Initialize default HIPAA requirements
def initialize_hipaa_requirements(registry: ComplianceRegistry) -> None:
    """Initialize default HIPAA compliance requirements."""
    # Access Control
    req = ComplianceRequirement(
        id="hipaa-164-312-a-1",
        framework=ComplianceFramework.HIPAA,
        title="Access Control",
        description="Implement technical policies and procedures for electronic information systems that maintain electronic protected health information to allow access only to those persons or software programs that have been granted access rights.",
        category="Security",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.AUTHORIZATION,
        status=AuditEventStatus.FAILURE
    )
    registry.register_requirement(req)
    
    # Audit Controls
    req = ComplianceRequirement(
        id="hipaa-164-312-b",
        framework=ComplianceFramework.HIPAA,
        title="Audit Controls",
        description="Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems that contain or use electronic protected health information.",
        category="Audit",
        severity="Medium"
    )
    req.add_audit_query(
        event_type=AuditEventType.SYSTEM_OPERATION,
        action="audit_system_check",
        status=AuditEventStatus.SUCCESS
    )
    registry.register_requirement(req)
    
    # Integrity
    req = ComplianceRequirement(
        id="hipaa-164-312-c-1",
        framework=ComplianceFramework.HIPAA,
        title="Integrity",
        description="Implement policies and procedures to protect electronic protected health information from improper alteration or destruction.",
        category="Data Protection",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.DATA_MODIFICATION,
        status=AuditEventStatus.FAILURE
    )
    registry.register_requirement(req)
    
    # Person or Entity Authentication
    req = ComplianceRequirement(
        id="hipaa-164-312-d",
        framework=ComplianceFramework.HIPAA,
        title="Person or Entity Authentication",
        description="Implement procedures to verify that a person or entity seeking access to electronic protected health information is the one claimed.",
        category="Authentication",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.AUTHENTICATION,
        status=AuditEventStatus.FAILURE
    )
    registry.register_requirement(req)

# Initialize default SOC2 requirements
def initialize_soc2_requirements(registry: ComplianceRegistry) -> None:
    """Initialize default SOC2 compliance requirements."""
    # Access Control
    req = ComplianceRequirement(
        id="soc2-cc5-1",
        framework=ComplianceFramework.SOC2,
        title="Access Control",
        description="The entity defines and implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events to meet the entity's objectives.",
        category="Security",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.AUTHORIZATION,
        status=AuditEventStatus.FAILURE
    )
    registry.register_requirement(req)
    
    # System Operations
    req = ComplianceRequirement(
        id="soc2-cc7-1",
        framework=ComplianceFramework.SOC2,
        title="System Operations",
        description="The entity monitors system components and the operation of those components for anomalies that are indicative of malicious acts, natural disasters, and errors affecting the entity's ability to meet its objectives.",
        category="Monitoring",
        severity="Medium"
    )
    req.add_audit_query(
        event_type=AuditEventType.SYSTEM_OPERATION,
        action="monitoring_check",
        status=AuditEventStatus.SUCCESS
    )
    registry.register_requirement(req)
    
    # Change Management
    req = ComplianceRequirement(
        id="soc2-cc8-1",
        framework=ComplianceFramework.SOC2,
        title="Change Management",
        description="The entity authorizes, designs, develops or acquires, configures, documents, tests, approves, and implements changes to infrastructure, data, software, and procedures to meet its objectives.",
        category="Change Management",
        severity="Medium"
    )
    req.add_audit_query(
        event_type=AuditEventType.CONFIGURATION_CHANGE,
        status=AuditEventStatus.SUCCESS
    )
    registry.register_requirement(req)
    
    # Risk Mitigation
    req = ComplianceRequirement(
        id="soc2-cc9-1",
        framework=ComplianceFramework.SOC2,
        title="Risk Mitigation",
        description="The entity identifies, selects, and develops risk mitigation activities for risks arising from potential business disruptions.",
        category="Risk Management",
        severity="High"
    )
    req.add_audit_query(
        event_type=AuditEventType.COMPLIANCE_EVENT,
        action="risk_assessment",
        status=AuditEventStatus.SUCCESS
    )
    registry.register_requirement(req)

# Initialize all default requirements
def initialize_default_requirements(registry: ComplianceRegistry) -> None:
    """Initialize all default compliance requirements."""
    initialize_gdpr_requirements(registry)
    initialize_hipaa_requirements(registry)
    initialize_soc2_requirements(registry)
    logger.info("Initialized default compliance requirements")
