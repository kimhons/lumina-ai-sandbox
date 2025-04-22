"""
Role-Based Access Control (RBAC) module for Lumina AI.

This module provides role-based access control for securing
resources and operations within the system.
"""

import os
import json
import time
from typing import Dict, Any, Optional, List, Set, Tuple
import logging

class RBACManager:
    """Manages role-based access control for Lumina AI."""
    
    def __init__(self, persist_dir: str = "./data/rbac"):
        """
        Initialize the RBAC manager.
        
        Args:
            persist_dir: Directory to persist RBAC data
        """
        self.persist_dir = persist_dir
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.permissions: Dict[str, Dict[str, Any]] = {}
        self.role_permissions: Dict[str, Set[str]] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create persistence directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Load existing data if available
        self._load()
        
        # Initialize default roles and permissions if none exist
        if not self.roles:
            self._initialize_defaults()
    
    def create_role(self, 
                   role_id: str, 
                   name: str, 
                   description: str = "") -> Tuple[bool, str]:
        """
        Create a new role.
        
        Args:
            role_id: Unique identifier for the role
            name: Display name for the role
            description: Description of the role
            
        Returns:
            Tuple of (success, message)
        """
        # Check if role already exists
        if role_id in self.roles:
            return False, f"Role '{role_id}' already exists"
        
        # Create role
        self.roles[role_id] = {
            "id": role_id,
            "name": name,
            "description": description,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Initialize empty permission set for this role
        self.role_permissions[role_id] = set()
        
        # Persist changes
        self._save()
        
        return True, f"Role '{role_id}' created successfully"
    
    def create_permission(self, 
                         permission_id: str, 
                         name: str, 
                         description: str = "",
                         resource: str = "*",
                         action: str = "*") -> Tuple[bool, str]:
        """
        Create a new permission.
        
        Args:
            permission_id: Unique identifier for the permission
            name: Display name for the permission
            description: Description of the permission
            resource: Resource the permission applies to (e.g., "users", "conversations")
            action: Action the permission allows (e.g., "read", "write", "delete")
            
        Returns:
            Tuple of (success, message)
        """
        # Check if permission already exists
        if permission_id in self.permissions:
            return False, f"Permission '{permission_id}' already exists"
        
        # Create permission
        self.permissions[permission_id] = {
            "id": permission_id,
            "name": name,
            "description": description,
            "resource": resource,
            "action": action,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Persist changes
        self._save()
        
        return True, f"Permission '{permission_id}' created successfully"
    
    def assign_permission_to_role(self, 
                                 role_id: str, 
                                 permission_id: str) -> Tuple[bool, str]:
        """
        Assign a permission to a role.
        
        Args:
            role_id: Role identifier
            permission_id: Permission identifier
            
        Returns:
            Tuple of (success, message)
        """
        # Check if role exists
        if role_id not in self.roles:
            return False, f"Role '{role_id}' does not exist"
        
        # Check if permission exists
        if permission_id not in self.permissions:
            return False, f"Permission '{permission_id}' does not exist"
        
        # Assign permission to role
        self.role_permissions.setdefault(role_id, set()).add(permission_id)
        
        # Persist changes
        self._save()
        
        return True, f"Permission '{permission_id}' assigned to role '{role_id}'"
    
    def remove_permission_from_role(self, 
                                   role_id: str, 
                                   permission_id: str) -> Tuple[bool, str]:
        """
        Remove a permission from a role.
        
        Args:
            role_id: Role identifier
            permission_id: Permission identifier
            
        Returns:
            Tuple of (success, message)
        """
        # Check if role exists
        if role_id not in self.roles:
            return False, f"Role '{role_id}' does not exist"
        
        # Check if permission exists
        if permission_id not in self.permissions:
            return False, f"Permission '{permission_id}' does not exist"
        
        # Check if role has this permission
        if permission_id not in self.role_permissions.get(role_id, set()):
            return False, f"Role '{role_id}' does not have permission '{permission_id}'"
        
        # Remove permission from role
        self.role_permissions[role_id].remove(permission_id)
        
        # Persist changes
        self._save()
        
        return True, f"Permission '{permission_id}' removed from role '{role_id}'"
    
    def assign_role_to_user(self, 
                           user_id: str, 
                           role_id: str) -> Tuple[bool, str]:
        """
        Assign a role to a user.
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            
        Returns:
            Tuple of (success, message)
        """
        # Check if role exists
        if role_id not in self.roles:
            return False, f"Role '{role_id}' does not exist"
        
        # Assign role to user
        self.user_roles.setdefault(user_id, set()).add(role_id)
        
        # Persist changes
        self._save()
        
        return True, f"Role '{role_id}' assigned to user '{user_id}'"
    
    def remove_role_from_user(self, 
                             user_id: str, 
                             role_id: str) -> Tuple[bool, str]:
        """
        Remove a role from a user.
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user has any roles
        if user_id not in self.user_roles:
            return False, f"User '{user_id}' has no roles assigned"
        
        # Check if user has this role
        if role_id not in self.user_roles[user_id]:
            return False, f"User '{user_id}' does not have role '{role_id}'"
        
        # Remove role from user
        self.user_roles[user_id].remove(role_id)
        
        # Clean up if user has no more roles
        if not self.user_roles[user_id]:
            del self.user_roles[user_id]
        
        # Persist changes
        self._save()
        
        return True, f"Role '{role_id}' removed from user '{user_id}'"
    
    def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all roles assigned to a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of role objects
        """
        role_ids = self.user_roles.get(user_id, set())
        return [self.roles[role_id] for role_id in role_ids if role_id in self.roles]
    
    def get_role_permissions(self, role_id: str) -> List[Dict[str, Any]]:
        """
        Get all permissions assigned to a role.
        
        Args:
            role_id: Role identifier
            
        Returns:
            List of permission objects
        """
        permission_ids = self.role_permissions.get(role_id, set())
        return [self.permissions[perm_id] for perm_id in permission_ids if perm_id in self.permissions]
    
    def get_user_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all permissions a user has through their roles.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of permission objects
        """
        role_ids = self.user_roles.get(user_id, set())
        permission_ids = set()
        
        # Collect all permissions from all roles
        for role_id in role_ids:
            permission_ids.update(self.role_permissions.get(role_id, set()))
        
        return [self.permissions[perm_id] for perm_id in permission_ids if perm_id in self.permissions]
    
    def check_permission(self, 
                        user_id: str, 
                        permission_id: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: User identifier
            permission_id: Permission identifier
            
        Returns:
            True if user has the permission, False otherwise
        """
        # Get user roles
        role_ids = self.user_roles.get(user_id, set())
        
        # Check if any role has the permission
        for role_id in role_ids:
            if permission_id in self.role_permissions.get(role_id, set()):
                return True
        
        return False
    
    def check_resource_action(self, 
                             user_id: str, 
                             resource: str, 
                             action: str) -> bool:
        """
        Check if a user has permission to perform an action on a resource.
        
        Args:
            user_id: User identifier
            resource: Resource to check
            action: Action to check
            
        Returns:
            True if user has permission, False otherwise
        """
        # Get all user permissions
        user_permissions = self.get_user_permissions(user_id)
        
        # Check for exact match
        for permission in user_permissions:
            perm_resource = permission["resource"]
            perm_action = permission["action"]
            
            # Check for exact match or wildcard
            resource_match = perm_resource == resource or perm_resource == "*"
            action_match = perm_action == action or perm_action == "*"
            
            if resource_match and action_match:
                return True
        
        return False
    
    def _initialize_defaults(self) -> None:
        """Initialize default roles and permissions."""
        # Create default roles
        self.create_role("admin", "Administrator", "Full system access")
        self.create_role("user", "Standard User", "Regular user access")
        self.create_role("guest", "Guest", "Limited read-only access")
        
        # Create default permissions
        self.create_permission("system.admin", "System Administration", "Full system administration", "*", "*")
        self.create_permission("users.read", "Read Users", "View user information", "users", "read")
        self.create_permission("users.write", "Modify Users", "Create and update users", "users", "write")
        self.create_permission("users.delete", "Delete Users", "Delete users", "users", "delete")
        self.create_permission("conversations.read", "Read Conversations", "View conversations", "conversations", "read")
        self.create_permission("conversations.write", "Create Conversations", "Create and update conversations", "conversations", "write")
        self.create_permission("conversations.delete", "Delete Conversations", "Delete conversations", "conversations", "delete")
        
        # Assign permissions to roles
        self.assign_permission_to_role("admin", "system.admin")
        
        self.assign_permission_to_role("user", "users.read")
        self.assign_permission_to_role("user", "conversations.read")
        self.assign_permission_to_role("user", "conversations.write")
        self.assign_permission_to_role("user", "conversations.delete")
        
        self.assign_permission_to_role("guest", "conversations.read")
    
    def _save(self) -> None:
        """Save RBAC data to disk."""
        data = {
            "roles": self.roles,
            "permissions": self.permissions,
            "role_permissions": {k: list(v) for k, v in self.role_permissions.items()},
            "user_roles": {k: list(v) for k, v in self.user_roles.items()}
        }
        
        with open(os.path.join(self.persist_dir, "rbac_data.json"), "w") as f:
            json.dump(data, f)
    
    def _load(self) -> None:
        """Load RBAC data from disk."""
        try:
            file_path = os.path.join(self.persist_dir, "rbac_data.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                self.roles = data.get("roles", {})
                self.permissions = data.get("permissions", {})
                self.role_permissions = {k: set(v) for k, v in data.get("role_permissions", {}).items()}
                self.user_roles = {k: set(v) for k, v in data.get("user_roles", {}).items()}
        except Exception as e:
            self.logger.error(f"Error loading RBAC data: {e}")
