"""
Lumina AI Security Package - Access Control Module

This module implements fine-grained access control for Lumina AI, including:
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Context-Aware Authorization
- Resource-Level Permissions
- API and Service Access Control

Copyright (c) 2025 AlienNova Technologies. All rights reserved.
"""

from enum import Enum
import uuid
import time
import json
import logging
from typing import Dict, List, Set, Optional, Any, Union, Callable
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Permission(Enum):
    """Enumeration of possible permissions in the system."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"
    
    @classmethod
    def from_string(cls, permission_str: str) -> "Permission":
        """Convert string to Permission enum."""
        try:
            return cls(permission_str.lower())
        except ValueError:
            raise ValueError(f"Invalid permission: {permission_str}")

@dataclass
class Resource:
    """Represents a resource in the system that can be protected."""
    id: str
    type: str
    owner_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "owner_id": self.owner_id,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resource":
        """Create resource from dictionary."""
        return cls(
            id=data["id"],
            type=data["type"],
            owner_id=data["owner_id"],
            attributes=data.get("attributes", {})
        )

@dataclass
class Role:
    """Represents a role in the system with associated permissions."""
    id: str
    name: str
    description: str
    permissions: Dict[str, Set[Permission]] = field(default_factory=dict)
    parent_roles: List[str] = field(default_factory=list)
    
    def add_permission(self, resource_type: str, permission: Permission) -> None:
        """Add a permission for a resource type to this role."""
        if resource_type not in self.permissions:
            self.permissions[resource_type] = set()
        self.permissions[resource_type].add(permission)
    
    def remove_permission(self, resource_type: str, permission: Permission) -> None:
        """Remove a permission for a resource type from this role."""
        if resource_type in self.permissions and permission in self.permissions[resource_type]:
            self.permissions[resource_type].remove(permission)
            if not self.permissions[resource_type]:
                del self.permissions[resource_type]
    
    def has_permission(self, resource_type: str, permission: Permission) -> bool:
        """Check if role has a specific permission for a resource type."""
        return resource_type in self.permissions and permission in self.permissions[resource_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": {
                resource_type: [perm.value for perm in perms]
                for resource_type, perms in self.permissions.items()
            },
            "parent_roles": self.parent_roles
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """Create role from dictionary."""
        role = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            parent_roles=data.get("parent_roles", [])
        )
        
        for resource_type, perms in data.get("permissions", {}).items():
            for perm in perms:
                role.add_permission(resource_type, Permission.from_string(perm))
        
        return role

@dataclass
class User:
    """Represents a user in the system."""
    id: str
    username: str
    email: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    
    def add_role(self, role_id: str) -> None:
        """Add a role to this user."""
        if role_id not in self.roles:
            self.roles.append(role_id)
    
    def remove_role(self, role_id: str) -> None:
        """Remove a role from this user."""
        if role_id in self.roles:
            self.roles.remove(role_id)
    
    def has_role(self, role_id: str) -> bool:
        """Check if user has a specific role."""
        return role_id in self.roles
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "attributes": self.attributes,
            "roles": self.roles
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create user from dictionary."""
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            attributes=data.get("attributes", {}),
            roles=data.get("roles", [])
        )

@dataclass
class AccessPolicy:
    """Represents an access policy for attribute-based access control."""
    id: str
    name: str
    description: str
    resource_type: str
    effect: str  # "allow" or "deny"
    conditions: Dict[str, Any] = field(default_factory=dict)
    permissions: Set[Permission] = field(default_factory=set)
    
    def add_permission(self, permission: Permission) -> None:
        """Add a permission to this policy."""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from this policy."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type,
            "effect": self.effect,
            "conditions": self.conditions,
            "permissions": [perm.value for perm in self.permissions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessPolicy":
        """Create policy from dictionary."""
        policy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            resource_type=data["resource_type"],
            effect=data["effect"],
            conditions=data.get("conditions", {})
        )
        
        for perm in data.get("permissions", []):
            policy.add_permission(Permission.from_string(perm))
        
        return policy

@dataclass
class AuthorizationContext:
    """Represents the context for an authorization decision."""
    user: User
    resource: Resource
    action: Permission
    environment: Dict[str, Any] = field(default_factory=dict)
    request_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "user": self.user.to_dict(),
            "resource": self.resource.to_dict(),
            "action": self.action.value,
            "environment": self.environment,
            "request_time": self.request_time
        }

class AccessControlRegistry:
    """Registry for access control components."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.resources: Dict[str, Resource] = {}
        self.policies: Dict[str, AccessPolicy] = {}
    
    def register_user(self, user: User) -> None:
        """Register a user in the system."""
        self.users[user.id] = user
        logger.info(f"Registered user: {user.username} (ID: {user.id})")
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def register_role(self, role: Role) -> None:
        """Register a role in the system."""
        self.roles[role.id] = role
        logger.info(f"Registered role: {role.name} (ID: {role.id})")
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Get a role by ID."""
        return self.roles.get(role_id)
    
    def register_resource(self, resource: Resource) -> None:
        """Register a resource in the system."""
        self.resources[resource.id] = resource
        logger.info(f"Registered resource: {resource.type} (ID: {resource.id})")
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        return self.resources.get(resource_id)
    
    def register_policy(self, policy: AccessPolicy) -> None:
        """Register an access policy in the system."""
        self.policies[policy.id] = policy
        logger.info(f"Registered policy: {policy.name} (ID: {policy.id})")
    
    def get_policy(self, policy_id: str) -> Optional[AccessPolicy]:
        """Get a policy by ID."""
        return self.policies.get(policy_id)
    
    def get_all_roles_for_user(self, user_id: str) -> List[Role]:
        """Get all roles for a user, including inherited roles."""
        user = self.get_user(user_id)
        if not user:
            return []
        
        # Direct roles
        roles = [self.get_role(role_id) for role_id in user.roles if self.get_role(role_id)]
        
        # Add parent roles (handle inheritance)
        processed_roles = set()
        result = []
        
        def process_role(role):
            if role.id in processed_roles:
                return
            processed_roles.add(role.id)
            result.append(role)
            for parent_id in role.parent_roles:
                parent = self.get_role(parent_id)
                if parent:
                    process_role(parent)
        
        for role in roles:
            process_role(role)
        
        return result
    
    def get_policies_for_resource_type(self, resource_type: str) -> List[AccessPolicy]:
        """Get all policies applicable to a resource type."""
        return [policy for policy in self.policies.values() if policy.resource_type == resource_type]

class RBACAuthorizer:
    """Role-Based Access Control (RBAC) authorizer."""
    
    def __init__(self, registry: AccessControlRegistry):
        self.registry = registry
    
    def is_authorized(self, context: AuthorizationContext) -> bool:
        """Check if the user is authorized to perform the action on the resource using RBAC."""
        user = context.user
        resource = context.resource
        action = context.action
        
        # Get all roles for the user
        roles = self.registry.get_all_roles_for_user(user.id)
        
        # Check if any role has the required permission
        for role in roles:
            if role.has_permission(resource.type, action):
                logger.info(f"RBAC: User {user.username} authorized for {action.value} on {resource.type} via role {role.name}")
                return True
        
        logger.info(f"RBAC: User {user.username} not authorized for {action.value} on {resource.type}")
        return False

class ABACAuthorizer:
    """Attribute-Based Access Control (ABAC) authorizer."""
    
    def __init__(self, registry: AccessControlRegistry):
        self.registry = registry
    
    def evaluate_condition(self, condition: Dict[str, Any], context: AuthorizationContext) -> bool:
        """Evaluate a condition against the authorization context."""
        # Simple condition evaluator - can be extended for more complex conditions
        condition_type = condition.get("type")
        
        if condition_type == "string_equals":
            path = condition.get("path", "")
            value = condition.get("value", "")
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return current == value
        
        elif condition_type == "string_contains":
            path = condition.get("path", "")
            value = condition.get("value", "")
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return value in current
        
        elif condition_type == "numeric_equals":
            path = condition.get("path", "")
            value = condition.get("value", 0)
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return current == value
        
        elif condition_type == "numeric_greater_than":
            path = condition.get("path", "")
            value = condition.get("value", 0)
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return current > value
        
        elif condition_type == "numeric_less_than":
            path = condition.get("path", "")
            value = condition.get("value", 0)
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return current < value
        
        elif condition_type == "bool_equals":
            path = condition.get("path", "")
            value = condition.get("value", False)
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return current == value
        
        elif condition_type == "time_greater_than":
            path = condition.get("path", "")
            value = condition.get("value", 0)
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return current > value
        
        elif condition_type == "time_less_than":
            path = condition.get("path", "")
            value = condition.get("value", 0)
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return current < value
        
        elif condition_type == "array_contains":
            path = condition.get("path", "")
            value = condition.get("value", "")
            
            # Extract the actual value from the context based on the path
            parts = path.split(".")
            current = context.to_dict()
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return False
            
            return value in current
        
        elif condition_type == "and":
            conditions = condition.get("conditions", [])
            return all(self.evaluate_condition(cond, context) for cond in conditions)
        
        elif condition_type == "or":
            conditions = condition.get("conditions", [])
            return any(self.evaluate_condition(cond, context) for cond in conditions)
        
        elif condition_type == "not":
            subcondition = condition.get("condition", {})
            return not self.evaluate_condition(subcondition, context)
        
        # Default to False for unknown condition types
        return False
    
    def is_authorized(self, context: AuthorizationContext) -> bool:
        """Check if the user is authorized to perform the action on the resource using ABAC."""
        resource = context.resource
        action = context.action
        
        # Get all policies for the resource type
        policies = self.registry.get_policies_for_resource_type(resource.type)
        
        # Check if any policy allows the action
        for policy in policies:
            # Skip if policy doesn't include the requested permission
            if action not in policy.permissions:
                continue
            
            # Evaluate policy conditions
            conditions_met = self.evaluate_condition({"type": "and", "conditions": policy.conditions}, context)
            
            if conditions_met:
                if policy.effect == "allow":
                    logger.info(f"ABAC: User {context.user.username} authorized for {action.value} on {resource.type} via policy {policy.name}")
                    return True
                elif policy.effect == "deny":
                    logger.info(f"ABAC: User {context.user.username} explicitly denied for {action.value} on {resource.type} via policy {policy.name}")
                    return False
        
        logger.info(f"ABAC: No applicable policies found for user {context.user.username}, action {action.value}, resource {resource.type}")
        return False

class ContextAwareAuthorizer:
    """Context-Aware Authorization authorizer."""
    
    def __init__(self, registry: AccessControlRegistry):
        self.registry = registry
    
    def is_authorized(self, context: AuthorizationContext) -> bool:
        """Check if the user is authorized based on context factors."""
        user = context.user
        resource = context.resource
        action = context.action
        environment = context.environment
        
        # Check time-based restrictions
        current_time = time.time()
        time_restrictions = environment.get("time_restrictions", {})
        
        if time_restrictions:
            start_time = time_restrictions.get("start_time")
            end_time = time_restrictions.get("end_time")
            
            if start_time and current_time < start_time:
                logger.info(f"Context: User {user.username} denied access due to time restriction (before start time)")
                return False
            
            if end_time and current_time > end_time:
                logger.info(f"Context: User {user.username} denied access due to time restriction (after end time)")
                return False
        
        # Check location-based restrictions
        location_restrictions = environment.get("location_restrictions", [])
        user_location = environment.get("user_location")
        
        if location_restrictions and user_location:
            if user_location not in location_restrictions:
                logger.info(f"Context: User {user.username} denied access due to location restriction")
                return False
        
        # Check device-based restrictions
        device_restrictions = environment.get("device_restrictions", [])
        user_device = environment.get("user_device")
        
        if device_restrictions and user_device:
            if user_device not in device_restrictions:
                logger.info(f"Context: User {user.username} denied access due to device restriction")
                return False
        
        # Check network-based restrictions
        network_restrictions = environment.get("network_restrictions", [])
        user_network = environment.get("user_network")
        
        if network_restrictions and user_network:
            if user_network not in network_restrictions:
                logger.info(f"Context: User {user.username} denied access due to network restriction")
                return False
        
        # Check risk score
        risk_threshold = environment.get("risk_threshold")
        user_risk_score = environment.get("user_risk_score")
        
        if risk_threshold is not None and user_risk_score is not None:
            if user_risk_score > risk_threshold:
                logger.info(f"Context: User {user.username} denied access due to high risk score")
                return False
        
        # If all context checks pass, the user is authorized
        logger.info(f"Context: User {user.username} authorized for {action.value} on {resource.type} based on context")
        return True

class AccessControlService:
    """Main service for access control."""
    
    def __init__(self):
        self.registry = AccessControlRegistry()
        self.rbac_authorizer = RBACAuthorizer(self.registry)
        self.abac_authorizer = ABACAuthorizer(self.registry)
        self.context_authorizer = ContextAwareAuthorizer(self.registry)
    
    def create_user(self, username: str, email: str, attributes: Dict[str, Any] = None) -> User:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=username,
            email=email,
            attributes=attributes or {}
        )
        self.registry.register_user(user)
        return user
    
    def create_role(self, name: str, description: str, parent_roles: List[str] = None) -> Role:
        """Create a new role."""
        role_id = str(uuid.uuid4())
        role = Role(
            id=role_id,
            name=name,
            description=description,
            parent_roles=parent_roles or []
        )
        self.registry.register_role(role)
        return role
    
    def create_resource(self, type: str, owner_id: str, attributes: Dict[str, Any] = None) -> Resource:
        """Create a new resource."""
        resource_id = str(uuid.uuid4())
        resource = Resource(
            id=resource_id,
            type=type,
            owner_id=owner_id,
            attributes=attributes or {}
        )
        self.registry.register_resource(resource)
        return resource
    
    def create_policy(self, name: str, description: str, resource_type: str, 
                     effect: str, conditions: Dict[str, Any], 
                     permissions: List[Permission]) -> AccessPolicy:
        """Create a new access policy."""
        policy_id = str(uuid.uuid4())
        policy = AccessPolicy(
            id=policy_id,
            name=name,
            description=description,
            resource_type=resource_type,
            effect=effect,
            conditions=conditions
        )
        
        for permission in permissions:
            policy.add_permission(permission)
        
        self.registry.register_policy(policy)
        return policy
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign a role to a user."""
        user = self.registry.get_user(user_id)
        role = self.registry.get_role(role_id)
        
        if not user or not role:
            return False
        
        user.add_role(role_id)
        logger.info(f"Assigned role {role.name} to user {user.username}")
        return True
    
    def add_permission_to_role(self, role_id: str, resource_type: str, permission: Permission) -> bool:
        """Add a permission to a role."""
        role = self.registry.get_role(role_id)
        
        if not role:
            return False
        
        role.add_permission(resource_type, permission)
        logger.info(f"Added permission {permission.value} for {resource_type} to role {role.name}")
        return True
    
    def is_authorized(self, user_id: str, resource_id: str, action: Permission, 
                     environment: Dict[str, Any] = None) -> bool:
        """Check if a user is authorized to perform an action on a resource."""
        user = self.registry.get_user(user_id)
        resource = self.registry.get_resource(resource_id)
        
        if not user or not resource:
            return False
        
        context = AuthorizationContext(
            user=user,
            resource=resource,
            action=action,
            environment=environment or {}
        )
        
        # First check context-aware authorization
        if not self.context_authorizer.is_authorized(context):
            return False
        
        # Then check ABAC (more specific)
        abac_result = self.abac_authorizer.is_authorized(context)
        if abac_result is not None:  # If ABAC gives a definitive answer
            return abac_result
        
        # Finally check RBAC (more general)
        return self.rbac_authorizer.is_authorized(context)
    
    def get_user_permissions(self, user_id: str, resource_type: str) -> Set[Permission]:
        """Get all permissions a user has for a resource type."""
        user = self.registry.get_user(user_id)
        if not user:
            return set()
        
        # Get permissions from roles (RBAC)
        roles = self.registry.get_all_roles_for_user(user_id)
        permissions = set()
        
        for role in roles:
            if resource_type in role.permissions:
                permissions.update(role.permissions[resource_type])
        
        return permissions
    
    def export_to_json(self, file_path: str) -> bool:
        """Export the access control configuration to a JSON file."""
        try:
            data = {
                "users": [user.to_dict() for user in self.registry.users.values()],
                "roles": [role.to_dict() for role in self.registry.roles.values()],
                "resources": [resource.to_dict() for resource in self.registry.resources.values()],
                "policies": [policy.to_dict() for policy in self.registry.policies.values()]
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported access control configuration to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export access control configuration: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """Import the access control configuration from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing data
            self.registry = AccessControlRegistry()
            self.rbac_authorizer = RBACAuthorizer(self.registry)
            self.abac_authorizer = ABACAuthorizer(self.registry)
            self.context_authorizer = ContextAwareAuthorizer(self.registry)
            
            # Import users
            for user_data in data.get("users", []):
                user = User.from_dict(user_data)
                self.registry.register_user(user)
            
            # Import roles
            for role_data in data.get("roles", []):
                role = Role.from_dict(role_data)
                self.registry.register_role(role)
            
            # Import resources
            for resource_data in data.get("resources", []):
                resource = Resource.from_dict(resource_data)
                self.registry.register_resource(resource)
            
            # Import policies
            for policy_data in data.get("policies", []):
                policy = AccessPolicy.from_dict(policy_data)
                self.registry.register_policy(policy)
            
            logger.info(f"Imported access control configuration from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import access control configuration: {e}")
            return False
