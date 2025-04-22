"""
Lumina AI Security Package - Tests for Advanced Security and Compliance System

This module implements comprehensive tests for the Advanced Security and Compliance system,
including tests for access control, audit logging, compliance reporting, encryption,
privacy controls, and ethical AI governance.

Copyright (c) 2025 AlienNova Technologies. All rights reserved.
"""

import unittest
import numpy as np
import time
import json
import os
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional

# Import security modules
from security.access_control import RoleBasedAccessControl, AttributeBasedAccessControl, ContextAwareAuthorization
from security.identity_management import IdentityManager, User, Role, Permission
from security.authentication import AuthenticationService, AuthenticationPolicy
from security.audit_logging import AuditLogger, AuditEvent, EventType, EventSeverity
from security.compliance_reporting import ComplianceReporter, ComplianceFramework, ComplianceRequirement
from security.encryption import EncryptionService, KeyManager, EncryptionAlgorithm
from security.privacy import PrivacyService, DataCategory, PrivacyTechnique
from security.ethical_governance import (
    EthicalGovernance, BiasDetector, FairnessAssessor, Explainer, HumanOversight,
    EthicalDecisionMaker, EthicalPrinciple, RiskLevel, DecisionType
)
from security.integration import SecurityIntegration

class TestAccessControl(unittest.TestCase):
    """Tests for the access control components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create roles
        self.admin_role = Role(id="admin", name="Administrator", description="System administrator")
        self.user_role = Role(id="user", name="User", description="Regular user")
        
        # Create permissions
        self.read_permission = Permission(id="read", name="Read", description="Read access")
        self.write_permission = Permission(id="write", name="Write", description="Write access")
        self.admin_permission = Permission(id="admin", name="Admin", description="Administrative access")
        
        # Assign permissions to roles
        self.admin_role.permissions = [self.read_permission, self.write_permission, self.admin_permission]
        self.user_role.permissions = [self.read_permission]
        
        # Create users
        self.admin_user = User(
            id="admin1",
            username="admin",
            email="admin@example.com",
            roles=[self.admin_role]
        )
        
        self.regular_user = User(
            id="user1",
            username="user",
            email="user@example.com",
            roles=[self.user_role]
        )
        
        # Create identity manager
        self.identity_manager = IdentityManager()
        self.identity_manager.add_user(self.admin_user)
        self.identity_manager.add_user(self.regular_user)
        
        # Create RBAC
        self.rbac = RoleBasedAccessControl(self.identity_manager)
        
        # Create ABAC
        self.abac = AttributeBasedAccessControl(self.identity_manager)
        
        # Create context-aware authorization
        self.context_auth = ContextAwareAuthorization(self.rbac, self.abac)
    
    def test_rbac_authorization(self):
        """Test role-based access control."""
        # Admin should have all permissions
        self.assertTrue(self.rbac.has_permission(self.admin_user.id, "read"))
        self.assertTrue(self.rbac.has_permission(self.admin_user.id, "write"))
        self.assertTrue(self.rbac.has_permission(self.admin_user.id, "admin"))
        
        # Regular user should only have read permission
        self.assertTrue(self.rbac.has_permission(self.regular_user.id, "read"))
        self.assertFalse(self.rbac.has_permission(self.regular_user.id, "write"))
        self.assertFalse(self.rbac.has_permission(self.regular_user.id, "admin"))
    
    def test_abac_authorization(self):
        """Test attribute-based access control."""
        # Create resource
        resource = {
            "id": "doc1",
            "type": "document",
            "owner": "user1",
            "department": "marketing",
            "classification": "confidential"
        }
        
        # Create policy
        policy = {
            "effect": "allow",
            "actions": ["read"],
            "resources": ["document"],
            "conditions": {
                "StringEquals": {
                    "resource.owner": "user.id"
                }
            }
        }
        
        self.abac.add_policy(policy)
        
        # User should be able to read their own document
        self.assertTrue(self.abac.is_allowed(self.regular_user, "read", resource))
        
        # Admin should not be able to read user's document (based on this specific policy)
        self.assertFalse(self.abac.is_allowed(self.admin_user, "read", resource))
        
        # Add admin policy
        admin_policy = {
            "effect": "allow",
            "actions": ["read", "write", "delete"],
            "resources": ["*"],
            "conditions": {
                "StringEquals": {
                    "user.roles": "admin"
                }
            }
        }
        
        self.abac.add_policy(admin_policy)
        
        # Now admin should be able to read any document
        self.assertTrue(self.abac.is_allowed(self.admin_user, "read", resource))
        self.assertTrue(self.abac.is_allowed(self.admin_user, "write", resource))
    
    def test_context_aware_authorization(self):
        """Test context-aware authorization."""
        # Create resource
        resource = {
            "id": "doc1",
            "type": "document",
            "owner": "user1",
            "department": "marketing",
            "classification": "confidential"
        }
        
        # Create context
        context = {
            "time": time.time(),
            "ip_address": "192.168.1.1",
            "device": "desktop",
            "location": "office"
        }
        
        # Create context rule
        rule = {
            "effect": "deny",
            "actions": ["read", "write", "delete"],
            "resources": ["*"],
            "conditions": {
                "StringNotEquals": {
                    "context.location": "office"
                }
            }
        }
        
        self.context_auth.add_context_rule(rule)
        
        # User should be able to access from office
        self.assertTrue(self.context_auth.authorize(
            self.regular_user.id, "read", resource, context
        ))
        
        # User should not be able to access from home
        home_context = context.copy()
        home_context["location"] = "home"
        
        self.assertFalse(self.context_auth.authorize(
            self.regular_user.id, "read", resource, home_context
        ))
        
        # Add exception for admins
        admin_rule = {
            "effect": "allow",
            "actions": ["read", "write", "delete"],
            "resources": ["*"],
            "conditions": {
                "StringEquals": {
                    "user.roles": "admin"
                }
            }
        }
        
        self.context_auth.add_context_rule(admin_rule)
        
        # Admin should be able to access from anywhere
        self.assertTrue(self.context_auth.authorize(
            self.admin_user.id, "read", resource, home_context
        ))

class TestAuditLogging(unittest.TestCase):
    """Tests for the audit logging components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create audit logger
        self.audit_logger = AuditLogger()
    
    def test_log_event(self):
        """Test logging an audit event."""
        # Create event
        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            user_id="user1",
            resource_id="resource1",
            action="login",
            status="success",
            severity=EventSeverity.INFO,
            details={"ip_address": "192.168.1.1"}
        )
        
        # Log event
        self.audit_logger.log_event(event)
        
        # Verify event was logged
        events = self.audit_logger.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, EventType.AUTHENTICATION)
        self.assertEqual(events[0].user_id, "user1")
        self.assertEqual(events[0].action, "login")
    
    def test_filter_events(self):
        """Test filtering audit events."""
        # Create and log multiple events
        event1 = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            user_id="user1",
            resource_id="resource1",
            action="login",
            status="success",
            severity=EventSeverity.INFO,
            details={"ip_address": "192.168.1.1"}
        )
        
        event2 = AuditEvent(
            event_type=EventType.AUTHORIZATION,
            user_id="user1",
            resource_id="resource2",
            action="read",
            status="denied",
            severity=EventSeverity.WARNING,
            details={"reason": "insufficient_permissions"}
        )
        
        event3 = AuditEvent(
            event_type=EventType.DATA_ACCESS,
            user_id="user2",
            resource_id="resource3",
            action="read",
            status="success",
            severity=EventSeverity.INFO,
            details={"data_type": "customer_record"}
        )
        
        self.audit_logger.log_event(event1)
        self.audit_logger.log_event(event2)
        self.audit_logger.log_event(event3)
        
        # Filter by user
        user1_events = self.audit_logger.filter_events(user_id="user1")
        self.assertEqual(len(user1_events), 2)
        
        # Filter by event type
        auth_events = self.audit_logger.filter_events(event_type=EventType.AUTHENTICATION)
        self.assertEqual(len(auth_events), 1)
        
        # Filter by action
        read_events = self.audit_logger.filter_events(action="read")
        self.assertEqual(len(read_events), 2)
        
        # Filter by status
        success_events = self.audit_logger.filter_events(status="success")
        self.assertEqual(len(success_events), 2)
        
        # Filter by severity
        warning_events = self.audit_logger.filter_events(severity=EventSeverity.WARNING)
        self.assertEqual(len(warning_events), 1)
        
        # Combined filters
        combined_events = self.audit_logger.filter_events(
            user_id="user1",
            action="read",
            status="denied"
        )
        self.assertEqual(len(combined_events), 1)
        self.assertEqual(combined_events[0].event_type, EventType.AUTHORIZATION)

class TestComplianceReporting(unittest.TestCase):
    """Tests for the compliance reporting components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create audit logger
        self.audit_logger = AuditLogger()
        
        # Create compliance reporter
        self.compliance_reporter = ComplianceReporter(self.audit_logger)
        
        # Add compliance frameworks
        self.gdpr = ComplianceFramework(
            id="gdpr",
            name="General Data Protection Regulation",
            description="EU data protection regulation"
        )
        
        self.hipaa = ComplianceFramework(
            id="hipaa",
            name="Health Insurance Portability and Accountability Act",
            description="US healthcare data protection regulation"
        )
        
        self.compliance_reporter.add_framework(self.gdpr)
        self.compliance_reporter.add_framework(self.hipaa)
        
        # Add compliance requirements
        self.gdpr_consent = ComplianceRequirement(
            id="gdpr-consent",
            framework_id="gdpr",
            name="Consent",
            description="Process personal data only with explicit consent",
            check_function="check_consent"
        )
        
        self.gdpr_breach = ComplianceRequirement(
            id="gdpr-breach",
            framework_id="gdpr",
            name="Breach Notification",
            description="Notify authorities of data breaches within 72 hours",
            check_function="check_breach_notification"
        )
        
        self.hipaa_access = ComplianceRequirement(
            id="hipaa-access",
            framework_id="hipaa",
            name="Access Controls",
            description="Implement technical policies and procedures for electronic PHI access",
            check_function="check_access_controls"
        )
        
        self.compliance_reporter.add_requirement(self.gdpr_consent)
        self.compliance_reporter.add_requirement(self.gdpr_breach)
        self.compliance_reporter.add_requirement(self.hipaa_access)
        
        # Mock check functions
        self.compliance_reporter.check_functions = {
            "check_consent": lambda: {"status": "pass", "evidence": "Consent records available"},
            "check_breach_notification": lambda: {"status": "warning", "evidence": "Process exists but not tested"},
            "check_access_controls": lambda: {"status": "pass", "evidence": "Access controls implemented"}
        }
    
    def test_generate_framework_report(self):
        """Test generating a compliance report for a framework."""
        # Generate GDPR report
        gdpr_report = self.compliance_reporter.generate_framework_report("gdpr")
        
        # Verify report
        self.assertEqual(gdpr_report["framework_id"], "gdpr")
        self.assertEqual(gdpr_report["framework_name"], "General Data Protection Regulation")
        self.assertEqual(len(gdpr_report["requirements"]), 2)
        
        # Check requirement results
        consent_result = next(r for r in gdpr_report["requirements"] if r["id"] == "gdpr-consent")
        breach_result = next(r for r in gdpr_report["requirements"] if r["id"] == "gdpr-breach")
        
        self.assertEqual(consent_result["status"], "pass")
        self.assertEqual(breach_result["status"], "warning")
        
        # Check overall status
        self.assertEqual(gdpr_report["overall_status"], "warning")
    
    def test_generate_requirement_report(self):
        """Test generating a compliance report for a specific requirement."""
        # Generate consent requirement report
        consent_report = self.compliance_reporter.generate_requirement_report("gdpr-consent")
        
        # Verify report
        self.assertEqual(consent_report["requirement_id"], "gdpr-consent")
        self.assertEqual(consent_report["requirement_name"], "Consent")
        self.assertEqual(consent_report["status"], "pass")
        self.assertEqual(consent_report["evidence"], "Consent records available")
    
    def test_export_report(self):
        """Test exporting a compliance report."""
        # Generate GDPR report
        gdpr_report = self.compliance_reporter.generate_framework_report("gdpr")
        
        # Export to JSON
        json_report = self.compliance_reporter.export_report(gdpr_report, "json")
        
        # Verify export
        self.assertIsInstance(json_report, str)
        
        # Parse JSON and verify content
        parsed_report = json.loads(json_report)
        self.assertEqual(parsed_report["framework_id"], "gdpr")
        self.assertEqual(len(parsed_report["requirements"]), 2)

class TestEncryption(unittest.TestCase):
    """Tests for the encryption components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create key manager
        self.key_manager = KeyManager()
        
        # Create encryption service
        self.encryption_service = EncryptionService(self.key_manager)
    
    def test_key_management(self):
        """Test key management functions."""
        # Generate key
        key_id = self.key_manager.generate_key(EncryptionAlgorithm.AES)
        
        # Verify key exists
        self.assertTrue(self.key_manager.key_exists(key_id))
        
        # Get key
        key = self.key_manager.get_key(key_id)
        self.assertIsNotNone(key)
        
        # Rotate key
        new_key_id = self.key_manager.rotate_key(key_id)
        self.assertNotEqual(key_id, new_key_id)
        
        # Verify both keys exist
        self.assertTrue(self.key_manager.key_exists(key_id))
        self.assertTrue(self.key_manager.key_exists(new_key_id))
        
        # Delete key
        self.key_manager.delete_key(key_id)
        self.assertFalse(self.key_manager.key_exists(key_id))
    
    def test_encryption_decryption(self):
        """Test encryption and decryption."""
        # Test data
        plaintext = "This is a secret message"
        
        # Encrypt with AES
        aes_key_id = self.key_manager.generate_key(EncryptionAlgorithm.AES)
        aes_ciphertext = self.encryption_service.encrypt(plaintext, aes_key_id)
        
        # Verify ciphertext is different from plaintext
        self.assertNotEqual(plaintext, aes_ciphertext)
        
        # Decrypt
        aes_decrypted = self.encryption_service.decrypt(aes_ciphertext, aes_key_id)
        
        # Verify decryption
        self.assertEqual(plaintext, aes_decrypted)
        
        # Encrypt with RSA
        rsa_key_id = self.key_manager.generate_key(EncryptionAlgorithm.RSA)
        rsa_ciphertext = self.encryption_service.encrypt(plaintext, rsa_key_id)
        
        # Verify ciphertext is different from plaintext
        self.assertNotEqual(plaintext, rsa_ciphertext)
        
        # Decrypt
        rsa_decrypted = self.encryption_service.decrypt(rsa_ciphertext, rsa_key_id)
        
        # Verify decryption
        self.assertEqual(plaintext, rsa_decrypted)
    
    def test_policy_based_encryption(self):
        """Test policy-based encryption."""
        # Create policy
        policy = {
            "data_type": "customer_data",
            "algorithm": EncryptionAlgorithm.AES,
            "key_rotation_period": 90  # days
        }
        
        self.encryption_service.add_encryption_policy(policy)
        
        # Encrypt with policy
        plaintext = "Customer: John Doe, SSN: 123-45-6789"
        ciphertext = self.encryption_service.encrypt_with_policy("customer_data", plaintext)
        
        # Verify ciphertext is different from plaintext
        self.assertNotEqual(plaintext, ciphertext)
        
        # Decrypt
        decrypted = self.encryption_service.decrypt_with_policy("customer_data", ciphertext)
        
        # Verify decryption
        self.assertEqual(plaintext, decrypted)

class TestPrivacy(unittest.TestCase):
    """Tests for the privacy components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create privacy service
        self.privacy_service = PrivacyService()
    
    def test_data_minimization(self):
        """Test data minimization."""
        # Original data
        original_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "address": "123 Main St, Anytown, USA",
            "ssn": "123-45-6789",
            "age": 35,
            "income": 75000
        }
        
        # Define fields to keep
        fields_to_keep = ["name", "email", "age"]
        
        # Apply data minimization
        minimized_data = self.privacy_service.minimize_data(original_data, fields_to_keep)
        
        # Verify minimized data
        self.assertEqual(len(minimized_data), 3)
        self.assertEqual(minimized_data["name"], "John Doe")
        self.assertEqual(minimized_data["email"], "john.doe@example.com")
        self.assertEqual(minimized_data["age"], 35)
        self.assertNotIn("ssn", minimized_data)
        self.assertNotIn("income", minimized_data)
    
    def test_anonymization(self):
        """Test anonymization."""
        # Original data
        original_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "address": "123 Main St, Anytown, USA",
            "ssn": "123-45-6789",
            "age": 35,
            "income": 75000
        }
        
        # Define anonymization rules
        anonymization_rules = {
            "name": {"technique": "mask", "params": {"mask_char": "*", "num_visible": 0}},
            "email": {"technique": "mask", "params": {"mask_char": "*", "num_visible": 3}},
            "phone": {"technique": "mask", "params": {"mask_char": "*", "num_visible": 4}},
            "ssn": {"technique": "mask", "params": {"mask_char": "*", "num_visible": 0}},
            "age": {"technique": "generalize", "params": {"ranges": [(0, 18), (19, 35), (36, 50), (51, 65), (66, 100)]}},
            "income": {"technique": "generalize", "params": {"ranges": [(0, 30000), (30001, 60000), (60001, 90000), (90001, 120000)]}}
        }
        
        # Apply anonymization
        anonymized_data = self.privacy_service.anonymize(original_data, anonymization_rules)
        
        # Verify anonymized data
        self.assertNotEqual(anonymized_data["name"], original_data["name"])
        self.assertNotEqual(anonymized_data["email"], original_data["email"])
        self.assertTrue(anonymized_data["email"].endswith("com"))  # Last 3 chars visible
        self.assertNotEqual(anonymized_data["phone"], original_data["phone"])
        self.assertTrue(anonymized_data["phone"].endswith("7890"))  # Last 4 digits visible
        self.assertNotEqual(anonymized_data["ssn"], original_data["ssn"])
        self.assertEqual(anonymized_data["age"], "19-35")  # Generalized age
        self.assertEqual(anonymized_data["income"], "60001-90000")  # Generalized income
    
    def test_pseudonymization(self):
        """Test pseudonymization."""
        # Original data
        original_data = {
            "user_id": "user123",
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
        
        # Define pseudonymization rules
        pseudonymization_rules = {
            "user_id": {"technique": "token"},
            "name": {"technique": "token"},
            "email": {"technique": "token"}
        }
        
        # Apply pseudonymization
        pseudonymized_data = self.privacy_service.pseudonymize(original_data, pseudonymization_rules)
        
        # Verify pseudonymized data
        self.assertNotEqual(pseudonymized_data["user_id"], original_data["user_id"])
        self.assertNotEqual(pseudonymized_data["name"], original_data["name"])
        self.assertNotEqual(pseudonymized_data["email"], original_data["email"])
        
        # Verify reversibility
        reversed_data = self.privacy_service.depseudonymize(pseudonymized_data)
        self.assertEqual(reversed_data["user_id"], original_data["user_id"])
        self.assertEqual(reversed_data["name"], original_data["name"])
        self.assertEqual(reversed_data["email"], original_data["email"])
    
    def test_differential_privacy(self):
        """Test differential privacy."""
        # Original data
        original_data = np.array([35, 42, 38, 40, 45, 50, 37, 41, 39, 36])
        
        # Apply differential privacy
        epsilon = 1.0  # Privacy parameter
        noisy_mean = self.privacy_service.differentially_private_mean(original_data, epsilon)
        
        # Verify noisy mean is close to actual mean
        actual_mean = np.mean(original_data)
        self.assertAlmostEqual(noisy_mean, actual_mean, delta=5.0)  # Allow some noise

class TestEthicalGovernance(unittest.TestCase):
    """Tests for the ethical governance components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create bias detector
        self.bias_detector = BiasDetector()
        
        # Create fairness assessor
        self.fairness_assessor = FairnessAssessor(self.bias_detector)
        
        # Create explainer
        self.explainer = Explainer()
        
        # Create human oversight
        self.human_oversight = HumanOversight()
        
        # Create ethical decision maker
        self.ethical_decision_maker = EthicalDecisionMaker(
            self.fairness_assessor, self.explainer, self.human_oversight
        )
        
        # Register ethical principles
        self.ethical_decision_maker.register_principle(EthicalPrinciple.FAIRNESS, 0.3, 0.7)
        self.ethical_decision_maker.register_principle(EthicalPrinciple.EXPLAINABILITY, 0.3, 0.7)
        self.ethical_decision_maker.register_principle(EthicalPrinciple.HUMAN_AUTONOMY, 0.2, 0.7)
        
        # Create ethical governance
        self.ethical_governance = EthicalGovernance(
            self.fairness_assessor, self.explainer, self.human_oversight, self.ethical_decision_maker
        )
    
    def test_bias_detection(self):
        """Test bias detection."""
        # Create test data
        predictions = np.array([1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        labels = np.array([1, 1, 0, 1, 0, 1, 0, 0, 1, 1])
        sensitive_attributes = {
            "gender": np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])  # 0=male, 1=female
        }
        
        # Detect bias
        bias_results = self.bias_detector.detect_bias(
            predictions, labels, sensitive_attributes, ["statistical_parity", "equal_opportunity"]
        )
        
        # Verify results
        self.assertIn("gender", bias_results)
        self.assertIn("statistical_parity", bias_results["gender"])
        self.assertIn("equal_opportunity", bias_results["gender"])
        
        # Values should be between 0 and 1
        self.assertGreaterEqual(bias_results["gender"]["statistical_parity"], 0)
        self.assertLessEqual(bias_results["gender"]["statistical_parity"], 1)
        self.assertGreaterEqual(bias_results["gender"]["equal_opportunity"], 0)
        self.assertLessEqual(bias_results["gender"]["equal_opportunity"], 1)
    
    def test_fairness_assessment(self):
        """Test fairness assessment."""
        # Create test data
        predictions = np.array([1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        labels = np.array([1, 1, 0, 1, 0, 1, 0, 0, 1, 1])
        sensitive_attributes = {
            "gender": np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])  # 0=male, 1=female
        }
        
        # Assess fairness
        fairness_results = self.fairness_assessor.assess_fairness(
            predictions, labels, sensitive_attributes, ["statistical_parity", "equal_opportunity"]
        )
        
        # Verify results
        self.assertIn("gender", fairness_results)
        self.assertIn("statistical_parity", fairness_results["gender"])
        self.assertIn("equal_opportunity", fairness_results["gender"])
        
        # Each metric should have value, threshold, and passes
        self.assertIn("value", fairness_results["gender"]["statistical_parity"])
        self.assertIn("threshold", fairness_results["gender"]["statistical_parity"])
        self.assertIn("passes", fairness_results["gender"]["statistical_parity"])
        
        # Get overall fairness
        overall = self.fairness_assessor.get_overall_fairness(fairness_results)
        
        # Verify overall results
        self.assertIn("score", overall)
        self.assertIn("status", overall)
        self.assertIn("passing_metrics", overall)
        self.assertIn("total_metrics", overall)
    
    def test_explainability(self):
        """Test explainability."""
        # Create mock model
        model = MagicMock()
        
        # Create instance
        instance = np.array([0.5, 0.3, 0.8, 0.2, 0.9])
        
        # Generate explanation
        explanation = self.explainer.explain(
            model, instance, "feature_importance",
            {"feature_names": ["feature1", "feature2", "feature3", "feature4", "feature5"]}
        )
        
        # Verify explanation
        self.assertEqual(explanation["method"], "feature_importance")
        self.assertIn("feature_names", explanation)
        self.assertIn("importances", explanation)
        self.assertIn("top_features", explanation)
        self.assertIn("top_importances", explanation)
        
        # Generate LIME explanation
        lime_explanation = self.explainer.explain(
            model, instance, "lime",
            {"feature_names": ["feature1", "feature2", "feature3", "feature4", "feature5"]}
        )
        
        # Verify LIME explanation
        self.assertEqual(lime_explanation["method"], "lime")
        self.assertIn("feature_names", lime_explanation)
        self.assertIn("coefficients", lime_explanation)
        self.assertIn("intercept", lime_explanation)
        self.assertIn("r2_score", lime_explanation)
    
    def test_human_oversight(self):
        """Test human oversight."""
        # Register decision
        decision_id = "decision1"
        application_id = "app1"
        decision_type = DecisionType.HUMAN_IN_LOOP
        prediction = 1
        confidence = 0.8
        context = {"user_id": "user1", "resource_id": "resource1"}
        explanation = {"method": "feature_importance", "top_features": ["feature1", "feature2"]}
        
        result = self.human_oversight.register_decision(
            decision_id, application_id, decision_type, prediction, confidence, context, explanation
        )
        
        # Verify result
        self.assertEqual(result["decision_id"], decision_id)
        self.assertEqual(result["status"], "pending")
        
        # Get pending decisions
        pending = self.human_oversight.get_pending_decisions()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["id"], decision_id)
        
        # Provide human feedback
        feedback = {"decision": 0, "reason": "Suspicious activity", "reviewer": "admin"}
        feedback_result = self.human_oversight.provide_human_feedback(decision_id, feedback)
        
        # Verify feedback result
        self.assertEqual(feedback_result["decision_id"], decision_id)
        self.assertEqual(feedback_result["status"], "completed")
        self.assertEqual(feedback_result["final_decision"], 0)
        
        # Get decision history
        history = self.human_oversight.get_decision_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["id"], decision_id)
        self.assertEqual(history[0]["final_decision"], 0)
        self.assertEqual(history[0]["human_feedback"]["reason"], "Suspicious activity")
    
    def test_ethical_decision_making(self):
        """Test ethical decision making."""
        # Create mock model
        model = MagicMock()
        
        # Create instance
        instance = np.array([0.5, 0.3, 0.8, 0.2, 0.9])
        
        # Create labels and sensitive attributes
        labels = np.array([1, 1, 0, 1, 0, 1, 0, 0, 1, 1])
        sensitive_attributes = {
            "gender": np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])  # 0=male, 1=female
        }
        
        # Create context
        context = {
            "user_id": "user1",
            "resource_id": "resource1",
            "feature_names": ["feature1", "feature2", "feature3", "feature4", "feature5"],
            "decision_type": DecisionType.HUMAN_IN_LOOP
        }
        
        # Make ethical decision
        decision_result = self.ethical_decision_maker.make_decision(
            "app1", "decision2", model, instance, labels, sensitive_attributes, context
        )
        
        # Verify decision result
        self.assertEqual(decision_result["decision_id"], "decision2")
        self.assertEqual(decision_result["application_id"], "app1")
        self.assertIn("prediction", decision_result)
        self.assertIn("confidence", decision_result)
        self.assertIn("explanation", decision_result)
        self.assertIn("ethical_evaluation", decision_result)
        self.assertIn("oversight_status", decision_result)
        
        # Verify ethical evaluation
        ethical_eval = decision_result["ethical_evaluation"]
        self.assertIn("overall", ethical_eval)
        self.assertIn("score", ethical_eval["overall"])
        self.assertIn("status", ethical_eval["overall"])
    
    def test_ethical_governance(self):
        """Test ethical governance."""
        # Register application
        application = self.ethical_governance.applications.get("app1")
        if not application:
            application = MagicMock()
            application.id = "app1"
            application.name = "Test Application"
            application.risk_level = RiskLevel.HIGH
            application.decision_type = DecisionType.HUMAN_IN_LOOP
            self.ethical_governance.applications["app1"] = application
        
        # Register requirement
        requirement = self.ethical_governance.requirements.get("req1")
        if not requirement:
            requirement = MagicMock()
            requirement.id = "req1"
            requirement.principle = EthicalPrinciple.FAIRNESS
            requirement.description = "Test requirement"
            requirement.risk_level = RiskLevel.HIGH
            requirement.decision_types = [DecisionType.HUMAN_IN_LOOP]
            self.ethical_governance.requirements["req1"] = requirement
        
        # Mock assessment method
        original_assess = self.ethical_governance._assess_requirement
        self.ethical_governance._assess_requirement = MagicMock(return_value=MagicMock(
            id="assessment1",
            application_id="app1",
            requirement_id="req1",
            timestamp=time.time(),
            status="pass",
            score=0.9,
            details={},
            to_dict=lambda: {
                "id": "assessment1",
                "application_id": "app1",
                "requirement_id": "req1",
                "timestamp": time.time(),
                "status": "pass",
                "score": 0.9,
                "details": {}
            }
        ))
        
        # Assess application
        assessment_result = self.ethical_governance.assess_application("app1")
        
        # Restore original method
        self.ethical_governance._assess_requirement = original_assess
        
        # Verify assessment result
        self.assertEqual(assessment_result["application_id"], "app1")
        self.assertIn("score", assessment_result)
        self.assertIn("status", assessment_result)
        self.assertIn("results", assessment_result)

class TestSecurityIntegration(unittest.TestCase):
    """Tests for the security integration components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock components
        self.rbac = MagicMock()
        self.abac = MagicMock()
        self.context_auth = MagicMock()
        self.identity_manager = MagicMock()
        self.authentication_service = MagicMock()
        self.audit_logger = MagicMock()
        self.compliance_reporter = MagicMock()
        self.encryption_service = MagicMock()
        self.privacy_service = MagicMock()
        self.ethical_governance = MagicMock()
        
        # Create security integration
        self.security_integration = SecurityIntegration(
            rbac=self.rbac,
            abac=self.abac,
            context_auth=self.context_auth,
            identity_manager=self.identity_manager,
            authentication_service=self.authentication_service,
            audit_logger=self.audit_logger,
            compliance_reporter=self.compliance_reporter,
            encryption_service=self.encryption_service,
            privacy_service=self.privacy_service,
            ethical_governance=self.ethical_governance
        )
    
    def test_enterprise_integration(self):
        """Test integration with Enterprise Integration system."""
        # Mock enterprise system
        enterprise_system = MagicMock()
        enterprise_system.id = "system1"
        enterprise_system.name = "CRM System"
        
        # Register enterprise system
        self.security_integration.register_enterprise_system(enterprise_system)
        
        # Verify system was registered
        self.assertIn(enterprise_system.id, self.security_integration.enterprise_systems)
        
        # Test secure data transfer
        data = {"customer_id": "cust123", "name": "John Doe", "ssn": "123-45-6789"}
        
        # Mock encryption and privacy services
        self.encryption_service.encrypt_with_policy.return_value = "encrypted_data"
        self.privacy_service.anonymize.return_value = {
            "customer_id": "cust123",
            "name": "****",
            "ssn": "****"
        }
        
        # Transfer data
        result = self.security_integration.secure_data_transfer(
            enterprise_system.id, "destination_system", data, 
            encrypt=True, anonymize=True
        )
        
        # Verify encryption and privacy services were called
        self.encryption_service.encrypt_with_policy.assert_called_once()
        self.privacy_service.anonymize.assert_called_once()
        
        # Verify audit logger was called
        self.audit_logger.log_event.assert_called_once()
    
    def test_multi_agent_integration(self):
        """Test integration with Multi-Agent Collaboration system."""
        # Mock agent team
        agent_team = MagicMock()
        agent_team.id = "team1"
        agent_team.name = "Analysis Team"
        agent_team.agents = ["agent1", "agent2", "agent3"]
        
        # Register agent team
        self.security_integration.register_agent_team(agent_team)
        
        # Verify team was registered
        self.assertIn(agent_team.id, self.security_integration.agent_teams)
        
        # Test secure collaboration
        # Mock authentication and authorization
        self.authentication_service.authenticate.return_value = True
        self.context_auth.authorize.return_value = True
        
        # Collaborate
        result = self.security_integration.secure_collaboration(
            "agent1", agent_team.id, "read", {"resource_id": "resource1"}
        )
        
        # Verify authentication and authorization were called
        self.authentication_service.authenticate.assert_called_once()
        self.context_auth.authorize.assert_called_once()
        
        # Verify audit logger was called
        self.audit_logger.log_event.assert_called_once()
    
    def test_learning_integration(self):
        """Test integration with Enhanced Learning system."""
        # Mock learning model
        learning_model = MagicMock()
        learning_model.id = "model1"
        learning_model.name = "Customer Churn Model"
        
        # Register learning model
        self.security_integration.register_learning_model(learning_model)
        
        # Verify model was registered
        self.assertIn(learning_model.id, self.security_integration.learning_models)
        
        # Test ethical learning
        # Mock ethical governance
        self.ethical_governance.assess_application.return_value = {
            "status": "pass",
            "score": 0.9
        }
        
        # Learn ethically
        result = self.security_integration.ethical_learning(
            learning_model.id, np.array([0.5, 0.3, 0.8]), np.array([1, 0, 1])
        )
        
        # Verify ethical governance was called
        self.ethical_governance.assess_application.assert_called_once()
        
        # Verify audit logger was called
        self.audit_logger.log_event.assert_called_once()
    
    def test_ui_integration(self):
        """Test integration with Adaptive UI system."""
        # Mock user
        user = MagicMock()
        user.id = "user1"
        user.username = "johndoe"
        
        # Test secure UI access
        # Mock authentication and authorization
        self.authentication_service.authenticate.return_value = True
        self.rbac.has_permission.return_value = True
        
        # Access UI
        result = self.security_integration.secure_ui_access(
            user.id, "view_dashboard"
        )
        
        # Verify authentication and authorization were called
        self.authentication_service.authenticate.assert_called_once()
        self.rbac.has_permission.assert_called_once()
        
        # Verify audit logger was called
        self.audit_logger.log_event.assert_called_once()
    
    def test_tool_integration(self):
        """Test integration with Expanded Tool Ecosystem."""
        # Mock tool
        tool = MagicMock()
        tool.id = "tool1"
        tool.name = "Data Analysis Tool"
        
        # Register tool
        self.security_integration.register_tool(tool)
        
        # Verify tool was registered
        self.assertIn(tool.id, self.security_integration.tools)
        
        # Test secure tool execution
        # Mock authentication and authorization
        self.authentication_service.authenticate.return_value = True
        self.abac.is_allowed.return_value = True
        
        # Execute tool
        result = self.security_integration.secure_tool_execution(
            "user1", tool.id, {"param1": "value1"}
        )
        
        # Verify authentication and authorization were called
        self.authentication_service.authenticate.assert_called_once()
        self.abac.is_allowed.assert_called_once()
        
        # Verify audit logger was called
        self.audit_logger.log_event.assert_called_once()

if __name__ == "__main__":
    unittest.main()
