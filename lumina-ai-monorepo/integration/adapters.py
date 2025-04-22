"""
Enterprise System Adapters for Lumina AI.

This module implements adapters for various enterprise systems,
providing system-specific implementations of the IntegrationSystem interface.
"""

import logging
import aiohttp
import json
import base64
import time
import asyncio
from typing import Dict, List, Any, Optional, Union
import urllib.parse

from .interfaces import IntegrationSystem, IntegrationConfig

logger = logging.getLogger(__name__)


class SalesforceAdapter(IntegrationSystem):
    """Adapter for Salesforce integration."""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize a new Salesforce adapter.
        
        Args:
            config: Configuration for the system
        """
        self.config = config
        self.client = None
        self.instance_url = config.connection_params.get("instance_url")
        self.api_version = config.connection_params.get("api_version", "v58.0")
        
    async def connect(self) -> bool:
        """
        Connect to Salesforce.
        
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            self.client = aiohttp.ClientSession()
            logger.info(f"Connected to Salesforce: {self.instance_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Salesforce: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from Salesforce.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Disconnected from Salesforce")
            
        return True
    
    async def is_connected(self) -> bool:
        """
        Check if connected to Salesforce.
        
        Returns:
            True if connected, False otherwise
        """
        return self.client is not None
    
    async def execute(self, operation: str, params: Dict[str, Any], credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation on Salesforce.
        
        Args:
            operation: Name of the operation to execute
            params: Parameters for the operation
            credentials: Authentication credentials
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If the operation fails
        """
        if not self.client:
            await self.connect()
            
        # Set authentication header
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Map operation to Salesforce API
        if operation == "query":
            return await self._execute_query(params, headers)
            
        elif operation == "create":
            return await self._execute_create(params, headers)
            
        elif operation == "update":
            return await self._execute_update(params, headers)
            
        elif operation == "delete":
            return await self._execute_delete(params, headers)
            
        elif operation == "bulk_query":
            return await self._execute_bulk_query(params, headers)
            
        elif operation == "register_webhook":
            return await self._register_webhook(params, headers)
            
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def _execute_query(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute a SOQL query.
        
        Args:
            params: Query parameters
            headers: Request headers
            
        Returns:
            Query results
        """
        soql = params.get("soql")
        if not soql:
            raise ValueError("SOQL query is required")
            
        # URL encode the query
        encoded_query = urllib.parse.quote(soql)
        url = f"{self.instance_url}/services/data/{self.api_version}/query?q={encoded_query}"
        
        async with self.client.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Salesforce query error: {error_text}")
                raise Exception(f"Salesforce query failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _execute_create(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a record.
        
        Args:
            params: Create parameters
            headers: Request headers
            
        Returns:
            Create result
        """
        sobject = params.get("sobject")
        data = params.get("data")
        
        if not sobject or not data:
            raise ValueError("sobject and data are required")
            
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}"
        
        async with self.client.post(url, headers=headers, json=data) as response:
            if response.status not in (201, 200):
                error_text = await response.text()
                logger.error(f"Salesforce create error: {error_text}")
                raise Exception(f"Salesforce create failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _execute_update(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Update a record.
        
        Args:
            params: Update parameters
            headers: Request headers
            
        Returns:
            Update result
        """
        sobject = params.get("sobject")
        record_id = params.get("record_id")
        data = params.get("data")
        
        if not sobject or not record_id or not data:
            raise ValueError("sobject, record_id, and data are required")
            
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        
        async with self.client.patch(url, headers=headers, json=data) as response:
            if response.status != 204:
                error_text = await response.text()
                logger.error(f"Salesforce update error: {error_text}")
                raise Exception(f"Salesforce update failed: {response.status} - {error_text}")
                
            return {"success": True, "id": record_id}
    
    async def _execute_delete(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Delete a record.
        
        Args:
            params: Delete parameters
            headers: Request headers
            
        Returns:
            Delete result
        """
        sobject = params.get("sobject")
        record_id = params.get("record_id")
        
        if not sobject or not record_id:
            raise ValueError("sobject and record_id are required")
            
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        
        async with self.client.delete(url, headers=headers) as response:
            if response.status != 204:
                error_text = await response.text()
                logger.error(f"Salesforce delete error: {error_text}")
                raise Exception(f"Salesforce delete failed: {response.status} - {error_text}")
                
            return {"success": True, "id": record_id}
    
    async def _execute_bulk_query(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute a bulk query.
        
        Args:
            params: Bulk query parameters
            headers: Request headers
            
        Returns:
            Bulk query results
        """
        soql = params.get("soql")
        if not soql:
            raise ValueError("SOQL query is required")
            
        # Create bulk job
        job_url = f"{self.instance_url}/services/data/{self.api_version}/jobs/query"
        job_data = {
            "operation": "query",
            "query": soql
        }
        
        async with self.client.post(job_url, headers=headers, json=job_data) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Salesforce bulk job creation error: {error_text}")
                raise Exception(f"Salesforce bulk job creation failed: {response.status} - {error_text}")
                
            job_result = await response.json()
            job_id = job_result.get("id")
            
        # Wait for job to complete
        job_status_url = f"{job_url}/{job_id}"
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            async with self.client.get(job_status_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Salesforce bulk job status error: {error_text}")
                    raise Exception(f"Salesforce bulk job status failed: {response.status} - {error_text}")
                    
                status_result = await response.json()
                state = status_result.get("state")
                
                if state == "JobComplete":
                    break
                elif state in ("Failed", "Aborted"):
                    raise Exception(f"Salesforce bulk job failed: {state}")
                    
            attempt += 1
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        if attempt >= max_attempts:
            raise Exception("Salesforce bulk job timed out")
            
        # Get results
        results_url = f"{job_status_url}/results"
        async with self.client.get(results_url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Salesforce bulk results error: {error_text}")
                raise Exception(f"Salesforce bulk results failed: {response.status} - {error_text}")
                
            results = await response.text()
            
        # Parse CSV results
        lines = results.strip().split("\n")
        if not lines:
            return {"records": []}
            
        headers = lines[0].split(",")
        records = []
        
        for line in lines[1:]:
            values = line.split(",")
            record = {}
            
            for i, header in enumerate(headers):
                if i < len(values):
                    record[header.strip('"')] = values[i].strip('"')
                    
            records.append(record)
            
        return {"records": records}
    
    async def _register_webhook(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Register a webhook.
        
        Args:
            params: Webhook parameters
            headers: Request headers
            
        Returns:
            Registration result
        """
        event_type = params.get("event_type")
        callback_url = params.get("callback_url")
        
        if not event_type or not callback_url:
            raise ValueError("event_type and callback_url are required")
            
        # Salesforce uses Platform Events for webhooks
        # This is a simplified implementation
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/PushTopic"
        
        # Create a PushTopic for the event
        push_topic_data = {
            "Name": f"LuminaAI_{event_type}_{int(time.time())}",
            "Query": f"SELECT Id FROM {event_type} WHERE SystemModstamp > YESTERDAY",
            "ApiVersion": self.api_version.replace("v", ""),
            "NotifyForOperationCreate": True,
            "NotifyForOperationUpdate": True,
            "NotifyForOperationDelete": True,
            "NotifyForOperationUndelete": True,
            "NotifyForFields": "All"
        }
        
        async with self.client.post(url, headers=headers, json=push_topic_data) as response:
            if response.status not in (201, 200):
                error_text = await response.text()
                logger.error(f"Salesforce PushTopic creation error: {error_text}")
                raise Exception(f"Salesforce PushTopic creation failed: {response.status} - {error_text}")
                
            result = await response.json()
            
        # In a real implementation, we would also need to:
        # 1. Set up a streaming client to listen for events
        # 2. Forward events to the callback URL
        # This is simplified for demonstration purposes
        
        return {
            "success": True,
            "id": result.get("id"),
            "name": push_topic_data["Name"]
        }


class MicrosoftTeamsAdapter(IntegrationSystem):
    """Adapter for Microsoft Teams integration."""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize a new Microsoft Teams adapter.
        
        Args:
            config: Configuration for the system
        """
        self.config = config
        self.client = None
        self.base_url = "https://graph.microsoft.com/v1.0"
        
    async def connect(self) -> bool:
        """
        Connect to Microsoft Teams.
        
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            self.client = aiohttp.ClientSession()
            logger.info("Connected to Microsoft Teams")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Microsoft Teams: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from Microsoft Teams.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Disconnected from Microsoft Teams")
            
        return True
    
    async def is_connected(self) -> bool:
        """
        Check if connected to Microsoft Teams.
        
        Returns:
            True if connected, False otherwise
        """
        return self.client is not None
    
    async def execute(self, operation: str, params: Dict[str, Any], credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation on Microsoft Teams.
        
        Args:
            operation: Name of the operation to execute
            params: Parameters for the operation
            credentials: Authentication credentials
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If the operation fails
        """
        if not self.client:
            await self.connect()
            
        # Set authentication header
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Map operation to Microsoft Graph API
        if operation == "get_teams":
            return await self._get_teams(params, headers)
            
        elif operation == "get_channels":
            return await self._get_channels(params, headers)
            
        elif operation == "send_message":
            return await self._send_message(params, headers)
            
        elif operation == "create_channel":
            return await self._create_channel(params, headers)
            
        elif operation == "register_webhook":
            return await self._register_webhook(params, headers)
            
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def _get_teams(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Get teams.
        
        Args:
            params: Query parameters
            headers: Request headers
            
        Returns:
            Teams list
        """
        url = f"{self.base_url}/me/joinedTeams"
        
        async with self.client.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Microsoft Teams get_teams error: {error_text}")
                raise Exception(f"Microsoft Teams get_teams failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _get_channels(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Get channels for a team.
        
        Args:
            params: Query parameters
            headers: Request headers
            
        Returns:
            Channels list
        """
        team_id = params.get("team_id")
        if not team_id:
            raise ValueError("team_id is required")
            
        url = f"{self.base_url}/teams/{team_id}/channels"
        
        async with self.client.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Microsoft Teams get_channels error: {error_text}")
                raise Exception(f"Microsoft Teams get_channels failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _send_message(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Send a message to a channel.
        
        Args:
            params: Message parameters
            headers: Request headers
            
        Returns:
            Message result
        """
        team_id = params.get("team_id")
        channel_id = params.get("channel_id")
        content = params.get("content")
        
        if not team_id or not channel_id or not content:
            raise ValueError("team_id, channel_id, and content are required")
            
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        
        message_data = {
            "body": {
                "content": content,
                "contentType": "html"
            }
        }
        
        async with self.client.post(url, headers=headers, json=message_data) as response:
            if response.status not in (201, 200):
                error_text = await response.text()
                logger.error(f"Microsoft Teams send_message error: {error_text}")
                raise Exception(f"Microsoft Teams send_message failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _create_channel(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a channel in a team.
        
        Args:
            params: Channel parameters
            headers: Request headers
            
        Returns:
            Channel creation result
        """
        team_id = params.get("team_id")
        display_name = params.get("display_name")
        description = params.get("description", "")
        
        if not team_id or not display_name:
            raise ValueError("team_id and display_name are required")
            
        url = f"{self.base_url}/teams/{team_id}/channels"
        
        channel_data = {
            "displayName": display_name,
            "description": description
        }
        
        async with self.client.post(url, headers=headers, json=channel_data) as response:
            if response.status not in (201, 200):
                error_text = await response.text()
                logger.error(f"Microsoft Teams create_channel error: {error_text}")
                raise Exception(f"Microsoft Teams create_channel failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _register_webhook(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Register a webhook.
        
        Args:
            params: Webhook parameters
            headers: Request headers
            
        Returns:
            Registration result
        """
        event_type = params.get("event_type")
        callback_url = params.get("callback_url")
        
        if not event_type or not callback_url:
            raise ValueError("event_type and callback_url are required")
            
        url = f"{self.base_url}/subscriptions"
        
        # Map event type to Microsoft Graph resource and change type
        resource_map = {
            "messages": "/teams/getAllMessages",
            "channels": "/teams/getAllChannels",
            "teams": "/teams"
        }
        
        resource = resource_map.get(event_type)
        if not resource:
            raise ValueError(f"Unsupported event type: {event_type}")
            
        subscription_data = {
            "changeType": "created,updated",
            "notificationUrl": callback_url,
            "resource": resource,
            "expirationDateTime": (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat() + "Z",
            "clientState": "LuminaAI_" + str(uuid.uuid4())
        }
        
        async with self.client.post(url, headers=headers, json=subscription_data) as response:
            if response.status not in (201, 200):
                error_text = await response.text()
                logger.error(f"Microsoft Teams register_webhook error: {error_text}")
                raise Exception(f"Microsoft Teams register_webhook failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result


class SapAdapter(IntegrationSystem):
    """Adapter for SAP integration."""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize a new SAP adapter.
        
        Args:
            config: Configuration for the system
        """
        self.config = config
        self.client = None
        self.base_url = config.connection_params.get("base_url")
        
    async def connect(self) -> bool:
        """
        Connect to SAP.
        
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            self.client = aiohttp.ClientSession()
            logger.info(f"Connected to SAP: {self.base_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to SAP: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from SAP.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Disconnected from SAP")
            
        return True
    
    async def is_connected(self) -> bool:
        """
        Check if connected to SAP.
        
        Returns:
            True if connected, False otherwise
        """
        return self.client is not None
    
    async def execute(self, operation: str, params: Dict[str, Any], credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation on SAP.
        
        Args:
            operation: Name of the operation to execute
            params: Parameters for the operation
            credentials: Authentication credentials
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If the operation fails
        """
        if not self.client:
            await self.connect()
            
        # Set authentication header
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Map operation to SAP OData API
        if operation == "get_entity":
            return await self._get_entity(params, headers)
            
        elif operation == "query_entities":
            return await self._query_entities(params, headers)
            
        elif operation == "create_entity":
            return await self._create_entity(params, headers)
            
        elif operation == "update_entity":
            return await self._update_entity(params, headers)
            
        elif operation == "delete_entity":
            return await self._delete_entity(params, headers)
            
        elif operation == "call_function":
            return await self._call_function(params, headers)
            
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def _get_entity(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Get an entity by key.
        
        Args:
            params: Query parameters
            headers: Request headers
            
        Returns:
            Entity data
        """
        entity_set = params.get("entity_set")
        key = params.get("key")
        
        if not entity_set or not key:
            raise ValueError("entity_set and key are required")
            
        url = f"{self.base_url}/{entity_set}('{key}')"
        
        async with self.client.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"SAP get_entity error: {error_text}")
                raise Exception(f"SAP get_entity failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _query_entities(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Query entities.
        
        Args:
            params: Query parameters
            headers: Request headers
            
        Returns:
            Query results
        """
        entity_set = params.get("entity_set")
        filter_query = params.get("filter")
        select = params.get("select")
        expand = params.get("expand")
        top = params.get("top")
        skip = params.get("skip")
        
        if not entity_set:
            raise ValueError("entity_set is required")
            
        url = f"{self.base_url}/{entity_set}"
        query_params = []
        
        if filter_query:
            query_params.append(f"$filter={urllib.parse.quote(filter_query)}")
            
        if select:
            query_params.append(f"$select={urllib.parse.quote(select)}")
            
        if expand:
            query_params.append(f"$expand={urllib.parse.quote(expand)}")
            
        if top:
            query_params.append(f"$top={top}")
            
        if skip:
            query_params.append(f"$skip={skip}")
            
        if query_params:
            url += "?" + "&".join(query_params)
            
        async with self.client.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"SAP query_entities error: {error_text}")
                raise Exception(f"SAP query_entities failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _create_entity(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Create an entity.
        
        Args:
            params: Entity parameters
            headers: Request headers
            
        Returns:
            Creation result
        """
        entity_set = params.get("entity_set")
        data = params.get("data")
        
        if not entity_set or not data:
            raise ValueError("entity_set and data are required")
            
        url = f"{self.base_url}/{entity_set}"
        
        async with self.client.post(url, headers=headers, json=data) as response:
            if response.status not in (201, 200):
                error_text = await response.text()
                logger.error(f"SAP create_entity error: {error_text}")
                raise Exception(f"SAP create_entity failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
    
    async def _update_entity(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Update an entity.
        
        Args:
            params: Update parameters
            headers: Request headers
            
        Returns:
            Update result
        """
        entity_set = params.get("entity_set")
        key = params.get("key")
        data = params.get("data")
        
        if not entity_set or not key or not data:
            raise ValueError("entity_set, key, and data are required")
            
        url = f"{self.base_url}/{entity_set}('{key}')"
        
        async with self.client.patch(url, headers=headers, json=data) as response:
            if response.status not in (204, 200):
                error_text = await response.text()
                logger.error(f"SAP update_entity error: {error_text}")
                raise Exception(f"SAP update_entity failed: {response.status} - {error_text}")
                
            # SAP OData might return 204 No Content
            if response.status == 204:
                return {"success": True, "id": key}
                
            result = await response.json()
            return result
    
    async def _delete_entity(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Delete an entity.
        
        Args:
            params: Delete parameters
            headers: Request headers
            
        Returns:
            Delete result
        """
        entity_set = params.get("entity_set")
        key = params.get("key")
        
        if not entity_set or not key:
            raise ValueError("entity_set and key are required")
            
        url = f"{self.base_url}/{entity_set}('{key}')"
        
        async with self.client.delete(url, headers=headers) as response:
            if response.status != 204:
                error_text = await response.text()
                logger.error(f"SAP delete_entity error: {error_text}")
                raise Exception(f"SAP delete_entity failed: {response.status} - {error_text}")
                
            return {"success": True, "id": key}
    
    async def _call_function(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Call a function import.
        
        Args:
            params: Function parameters
            headers: Request headers
            
        Returns:
            Function result
        """
        function_name = params.get("function_name")
        parameters = params.get("parameters", {})
        
        if not function_name:
            raise ValueError("function_name is required")
            
        # Build URL with parameters
        url = f"{self.base_url}/{function_name}"
        
        if parameters:
            param_strings = []
            for key, value in parameters.items():
                if isinstance(value, str):
                    param_strings.append(f"{key}='{urllib.parse.quote(value)}'")
                else:
                    param_strings.append(f"{key}={value}")
                    
            url += "?" + "&".join(param_strings)
            
        async with self.client.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"SAP call_function error: {error_text}")
                raise Exception(f"SAP call_function failed: {response.status} - {error_text}")
                
            result = await response.json()
            return result
