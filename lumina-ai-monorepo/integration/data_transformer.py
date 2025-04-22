"""
Enterprise Data Transformer for Lumina AI.

This module implements the data transformation components for enterprise integrations,
providing bidirectional conversion between internal and external data formats.
"""

import logging
import json
import jsonschema
from typing import Dict, List, Any, Optional, Union

from .interfaces import DataTransformer, IntegrationConfig

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Exception raised when data fails schema validation."""
    pass


class TransformationError(Exception):
    """Exception raised when data transformation fails."""
    pass


class SchemaRegistry:
    """Registry for schema definitions used in data transformation."""
    
    def __init__(self):
        """Initialize a new schema registry."""
        self.internal_schemas = {}
        self.external_schemas = {}
        
    def register_internal_schema(self, entity_type: str, schema: Dict[str, Any]):
        """
        Register an internal schema.
        
        Args:
            entity_type: Type of entity the schema applies to
            schema: JSON Schema definition
        """
        self.internal_schemas[entity_type] = schema
        logger.info(f"Registered internal schema for entity type: {entity_type}")
        
    def register_external_schema(self, system_type: str, entity_type: str, schema: Dict[str, Any]):
        """
        Register an external schema.
        
        Args:
            system_type: Type of external system
            entity_type: Type of entity the schema applies to
            schema: JSON Schema definition
        """
        key = f"{system_type}:{entity_type}"
        self.external_schemas[key] = schema
        logger.info(f"Registered external schema for {key}")
        
    def get_internal_schema(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Get an internal schema.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            The schema if found, None otherwise
        """
        return self.internal_schemas.get(entity_type)
        
    def get_external_schema(self, system_type: str, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Get an external schema.
        
        Args:
            system_type: Type of external system
            entity_type: Type of entity
            
        Returns:
            The schema if found, None otherwise
        """
        key = f"{system_type}:{entity_type}"
        return self.external_schemas.get(key)


class CanonicalDataModel:
    """Canonical data model for internal data representation."""
    
    def __init__(self, schema_registry: SchemaRegistry):
        """
        Initialize a new canonical data model.
        
        Args:
            schema_registry: Registry of schemas
        """
        self.schema_registry = schema_registry
        
    def validate(self, data: Dict[str, Any], entity_type: str) -> bool:
        """
        Validate data against the internal schema.
        
        Args:
            data: Data to validate
            entity_type: Type of entity
            
        Returns:
            True if validation succeeds
            
        Raises:
            SchemaValidationError: If validation fails
        """
        schema = self.schema_registry.get_internal_schema(entity_type)
        if not schema:
            logger.warning(f"No internal schema found for entity type: {entity_type}")
            return True
            
        try:
            jsonschema.validate(instance=data, schema=schema)
            return True
            
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Validation error for entity type {entity_type}: {str(e)}")
            raise SchemaValidationError(f"Data does not match internal schema for {entity_type}: {str(e)}")


class EnterpriseDataTransformer(DataTransformer):
    """
    Data transformer for enterprise integrations.
    
    This class is responsible for transforming data between internal and external formats,
    ensuring that data conforms to the expected schemas and formats.
    """
    
    def __init__(
        self,
        system_config: IntegrationConfig,
        schema_registry: SchemaRegistry,
        canonical_model: CanonicalDataModel
    ):
        """
        Initialize a new enterprise data transformer.
        
        Args:
            system_config: Configuration for the system
            schema_registry: Registry of schemas
            canonical_model: Canonical data model
        """
        self.system_config = system_config
        self.schema_registry = schema_registry
        self.canonical_model = canonical_model
        self.system_type = system_config.system_type
        self.transformation_rules = system_config.transform_params.get("rules", {})
        
    async def transform_to_external(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform data from internal format to external format.
        
        Args:
            data: Data in internal format
            
        Returns:
            Data in external format
            
        Raises:
            SchemaValidationError: If data fails schema validation
            TransformationError: If transformation fails
        """
        try:
            # Get entity type from data or default
            entity_type = data.get("_entity_type", "default")
            
            # Validate against internal schema
            self.canonical_model.validate(data, entity_type)
            
            # Apply transformation rules
            external_data = self._apply_transformation_rules(
                data, 
                direction="outbound",
                entity_type=entity_type
            )
            
            # Validate against external schema if available
            external_schema = self.schema_registry.get_external_schema(
                self.system_type,
                entity_type
            )
            
            if external_schema:
                try:
                    jsonschema.validate(instance=external_data, schema=external_schema)
                except jsonschema.exceptions.ValidationError as e:
                    logger.error(f"External schema validation error: {str(e)}")
                    raise SchemaValidationError(f"Data does not match external schema for {entity_type}: {str(e)}")
            
            return external_data
            
        except Exception as e:
            if not isinstance(e, (SchemaValidationError, TransformationError)):
                logger.error(f"Error transforming to external format: {str(e)}")
                raise TransformationError(f"Failed to transform to external format: {str(e)}")
            raise
        
    async def transform_to_internal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform data from external format to internal format.
        
        Args:
            data: Data in external format
            
        Returns:
            Data in internal format
            
        Raises:
            SchemaValidationError: If data fails schema validation
            TransformationError: If transformation fails
        """
        try:
            # Determine entity type from data or metadata
            entity_type = data.get("_entity_type", "default")
            
            # Validate against external schema if available
            external_schema = self.schema_registry.get_external_schema(
                self.system_type,
                entity_type
            )
            
            if external_schema:
                try:
                    jsonschema.validate(instance=data, schema=external_schema)
                except jsonschema.exceptions.ValidationError as e:
                    logger.warning(f"External data does not match schema: {str(e)}")
                    # Continue with transformation despite validation failure
            
            # Apply transformation rules
            internal_data = self._apply_transformation_rules(
                data, 
                direction="inbound",
                entity_type=entity_type
            )
            
            # Add metadata
            if "_metadata" not in internal_data:
                internal_data["_metadata"] = {}
                
            internal_data["_metadata"]["source_system"] = self.system_config.system_id
            internal_data["_metadata"]["source_system_type"] = self.system_type
            internal_data["_entity_type"] = entity_type
            
            # Validate against internal schema
            self.canonical_model.validate(internal_data, entity_type)
            
            return internal_data
            
        except Exception as e:
            if not isinstance(e, (SchemaValidationError, TransformationError)):
                logger.error(f"Error transforming to internal format: {str(e)}")
                raise TransformationError(f"Failed to transform to internal format: {str(e)}")
            raise
    
    def _apply_transformation_rules(
        self,
        data: Dict[str, Any],
        direction: str,
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Apply transformation rules to data.
        
        Args:
            data: Data to transform
            direction: Direction of transformation ('inbound' or 'outbound')
            entity_type: Type of entity
            
        Returns:
            Transformed data
        """
        # Get rules for this entity type and direction
        entity_rules = self.transformation_rules.get(entity_type, {})
        direction_rules = entity_rules.get(direction, {})
        
        if not direction_rules:
            # No specific rules, return copy of original data
            return dict(data)
            
        # Start with empty result or copy of original based on mode
        mode = direction_rules.get("mode", "selective")
        result = {} if mode == "selective" else dict(data)
        
        # Apply field mappings
        field_mappings = direction_rules.get("field_mappings", {})
        for source_field, target_field in field_mappings.items():
            if source_field in data:
                result[target_field] = data[source_field]
                
        # Apply value transformations
        value_transformations = direction_rules.get("value_transformations", {})
        for field, transformation in value_transformations.items():
            if field in result:
                result[field] = self._transform_value(result[field], transformation)
                
        # Apply default values for missing fields
        default_values = direction_rules.get("default_values", {})
        for field, default_value in default_values.items():
            if field not in result or result[field] is None:
                result[field] = default_value
                
        # Remove specified fields
        fields_to_remove = direction_rules.get("fields_to_remove", [])
        for field in fields_to_remove:
            if field in result:
                del result[field]
                
        return result
    
    def _transform_value(self, value: Any, transformation: Dict[str, Any]) -> Any:
        """
        Transform a value according to transformation rules.
        
        Args:
            value: Value to transform
            transformation: Transformation rules
            
        Returns:
            Transformed value
        """
        transform_type = transformation.get("type")
        
        if transform_type == "map":
            # Map value to another value
            value_map = transformation.get("map", {})
            default = transformation.get("default", value)
            return value_map.get(str(value), default)
            
        elif transform_type == "format":
            # Format string value
            format_string = transformation.get("format", "{}")
            try:
                return format_string.format(value)
            except Exception as e:
                logger.error(f"Error formatting value: {str(e)}")
                return value
                
        elif transform_type == "split":
            # Split string value
            delimiter = transformation.get("delimiter", ",")
            index = transformation.get("index", 0)
            try:
                parts = value.split(delimiter)
                return parts[index] if 0 <= index < len(parts) else value
            except Exception as e:
                logger.error(f"Error splitting value: {str(e)}")
                return value
                
        elif transform_type == "join":
            # Join list value
            delimiter = transformation.get("delimiter", ",")
            try:
                return delimiter.join(value)
            except Exception as e:
                logger.error(f"Error joining value: {str(e)}")
                return value
                
        elif transform_type == "boolean":
            # Convert to boolean
            true_values = transformation.get("true_values", ["true", "yes", "1", "y", "t"])
            if isinstance(value, str):
                return value.lower() in [v.lower() for v in true_values]
            return bool(value)
            
        elif transform_type == "number":
            # Convert to number
            try:
                return float(value)
            except Exception as e:
                logger.error(f"Error converting to number: {str(e)}")
                return 0
                
        elif transform_type == "string":
            # Convert to string
            try:
                return str(value)
            except Exception as e:
                logger.error(f"Error converting to string: {str(e)}")
                return ""
                
        # No transformation or unknown type
        return value


class TransformerFactory:
    """Factory for creating data transformers."""
    
    def __init__(self, schema_registry: SchemaRegistry, canonical_model: CanonicalDataModel):
        """
        Initialize a new transformer factory.
        
        Args:
            schema_registry: Registry of schemas
            canonical_model: Canonical data model
        """
        self.schema_registry = schema_registry
        self.canonical_model = canonical_model
        self.transformers = {}
        
    def create_transformer(self, system_config: IntegrationConfig) -> DataTransformer:
        """
        Create a data transformer for a system.
        
        Args:
            system_config: Configuration for the system
            
        Returns:
            The created transformer
        """
        system_id = system_config.system_id
        
        # Return cached transformer if available
        if system_id in self.transformers:
            return self.transformers[system_id]
            
        # Create new transformer
        transformer = EnterpriseDataTransformer(
            system_config=system_config,
            schema_registry=self.schema_registry,
            canonical_model=self.canonical_model
        )
        
        # Cache the transformer
        self.transformers[system_id] = transformer
        
        return transformer
        
    def remove_transformer(self, system_id: str) -> bool:
        """
        Remove a transformer from the cache.
        
        Args:
            system_id: ID of the system
            
        Returns:
            True if the transformer was removed, False otherwise
        """
        if system_id in self.transformers:
            del self.transformers[system_id]
            return True
            
        return False
        
    def clear_transformers(self):
        """Clear all cached transformers."""
        self.transformers = {}
