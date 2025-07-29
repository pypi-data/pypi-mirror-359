"""OPC-UA client implementation"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from asyncua import Client, Node, ua
from asyncua.common.node import Node as AsyncUaNode

from ..base import BaseDataSource, NodeValue, BrowseResult, ConnectionStatus
from ..exceptions import ConnectionError, ReadError, WriteError, BrowseError, TimeoutError

logger = logging.getLogger(__name__)


class OpcUaClient(BaseDataSource):
    """OPC-UA client implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OPC-UA client
        
        Args:
            config: Configuration dictionary with OPC-UA settings
        """
        super().__init__(config)
        self._client: Optional[Client] = None
        self._url = config.get("url")
        self._username = config.get("username")
        self._password = config.get("password")
        self._timeout = config.get("connection_timeout", 30.0)
        self._max_retries = config.get("max_retries", 3)
        self._retry_delay = config.get("retry_delay", 5.0)
        
        # Test node for connection health checks
        self._test_node_id = config.get("test_node_id") or "ns=0;i=84"  # Default to root node
        logger.debug(f"Using test node ID: {self._test_node_id}")
        
    async def connect(self) -> bool:
        """Connect to OPC-UA server"""
        if self._connected:
            return True
            
        async with self._connection_lock:
            if self._connected:  # Double-check after acquiring lock
                return True
                
            self._connection_status = ConnectionStatus.CONNECTING
            
            for attempt in range(self._max_retries + 1):
                try:
                    # Create client
                    self._client = Client(url=self._url)
                    
                    # Set timeout
                    self._client.session_timeout = self._timeout * 1000  # Convert to milliseconds
                    
                    # Connect
                    await asyncio.wait_for(self._client.connect(), timeout=self._timeout)
                    
                    # Authenticate if credentials provided
                    if self._username and self._password:
                        try:
                            # Set authentication credentials
                            self._client.set_user(self._username)
                            self._client.set_password(self._password)
                            logger.info(f"Set authentication credentials for user: {self._username}")
                        except Exception as auth_error:
                            logger.warning(f"Failed to set authentication credentials: {auth_error}")
                            # Continue without authentication if it fails
                    
                    # Test connection by trying to read the test node
                    if self._test_node_id:
                        try:
                            await self._client.get_node(self._test_node_id).read_value()
                        except ua.UaError as ua_error:
                            if "BadAttributeIdInvalid" in str(ua_error):
                                # Node exists but doesn't have a value - that's OK for connection test
                                logger.info(f"Test node {self._test_node_id} exists but has no value attribute - connection OK")
                            else:
                                # Re-raise other UA errors
                                raise
                    else:
                        logger.warning("No test node ID configured - skipping connection test")
                    
                    self._connected = True
                    self._connection_status = ConnectionStatus.CONNECTED
                    logger.info(f"Connected to OPC-UA server: {self._url}")
                    return True
                    
                except asyncio.TimeoutError:
                    error_msg = f"Connection timeout to {self._url}"
                    logger.warning(f"{error_msg} (attempt {attempt + 1}/{self._max_retries + 1})")
                    if attempt == self._max_retries:
                        self._connection_status = ConnectionStatus.ERROR
                        raise TimeoutError(error_msg, "connect", self._timeout)
                        
                except Exception as e:
                    error_msg = f"Failed to connect to {self._url}: {str(e)}"
                    logger.warning(f"{error_msg} (attempt {attempt + 1}/{self._max_retries + 1})")
                    if attempt == self._max_retries:
                        self._connection_status = ConnectionStatus.ERROR
                        raise ConnectionError(error_msg, {"url": self._url, "error": str(e)})
                
                # Wait before retry
                if attempt < self._max_retries:
                    await asyncio.sleep(self._retry_delay)
            
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from OPC-UA server"""
        if not self._connected:
            return True
            
        async with self._connection_lock:
            if not self._connected:  # Double-check after acquiring lock
                return True
                
            try:
                if self._client:
                    await self._client.disconnect()
                    self._client = None
                
                self._connected = False
                self._connection_status = ConnectionStatus.DISCONNECTED
                logger.info(f"Disconnected from OPC-UA server: {self._url}")
                return True
                
            except Exception as e:
                logger.error(f"Error disconnecting from {self._url}: {e}")
                self._connection_status = ConnectionStatus.ERROR
                return False
    
    async def read_node(self, node_id: str) -> Optional[NodeValue]:
        """Read a single node value"""
        if not await self.ensure_connected():
            return None
            
        try:
            node = self._client.get_node(node_id)
            value = await node.get_value()
            timestamp = await node.read_data_value()
            
            return NodeValue(
                node_id=node_id,
                value=value,
                timestamp=timestamp.SourceTimestamp.to_datetime() if timestamp.SourceTimestamp else datetime.now(),
                quality="GOOD" if timestamp.StatusCode.is_good() else "BAD"
            )
            
        except ua.UaError as e:
            raise ReadError(f"Failed to read node {node_id}: {str(e)}", node_id, {"ua_error": str(e)})
        except Exception as e:
            raise ReadError(f"Unexpected error reading node {node_id}: {str(e)}", node_id, {"error": str(e)})
    
    async def read_nodes(self, node_ids: List[str]) -> Dict[str, Optional[NodeValue]]:
        """Read multiple node values (bulk read)"""
        if not await self.ensure_connected():
            return {node_id: None for node_id in node_ids}
            
        results = {}
        
        try:
            # Create nodes list
            nodes = [self._client.get_node(node_id) for node_id in node_ids]
            
            # Bulk read
            values = await self._client.read_values(nodes)
            
            for i, node_id in enumerate(node_ids):
                try:
                    value = values[i]
                    timestamp = datetime.now()  # Bulk read doesn't provide individual timestamps
                    
                    results[node_id] = NodeValue(
                        node_id=node_id,
                        value=value,
                        timestamp=timestamp,
                        quality="GOOD"
                    )
                except Exception as e:
                    logger.warning(f"Failed to process node {node_id}: {e}")
                    results[node_id] = None
                    
        except Exception as e:
            logger.error(f"Bulk read failed: {e}")
            # Fallback to individual reads
            for node_id in node_ids:
                try:
                    results[node_id] = await self.read_node(node_id)
                except Exception as read_error:
                    logger.warning(f"Individual read failed for {node_id}: {read_error}")
                    results[node_id] = None
        
        return results
    
    async def write_node(self, node_id: str, value: Any) -> bool:
        """Write value to a node"""
        if not await self.ensure_connected():
            return False
            
        try:
            node = self._client.get_node(node_id)
            await node.write_value(value)
            logger.info(f"Successfully wrote value to node {node_id}")
            return True
            
        except ua.UaError as e:
            raise WriteError(f"Failed to write to node {node_id}: {str(e)}", node_id, value, {"ua_error": str(e)})
        except Exception as e:
            raise WriteError(f"Unexpected error writing to node {node_id}: {str(e)}", node_id, value, {"error": str(e)})
    
    async def browse(self, start_node: Optional[str] = None, max_depth: int = 1) -> List[BrowseResult]:
        """Browse available nodes"""
        if not await self.ensure_connected():
            return []
            
        try:
            # Get starting node
            if start_node:
                start_node_obj = self._client.get_node(start_node)
            else:
                start_node_obj = self._client.get_root_node()
            
            results = []
            await self._browse_recursive(start_node_obj, results, max_depth, 0)
            return results
            
        except Exception as e:
            raise BrowseError(f"Failed to browse nodes: {str(e)}", start_node, {"error": str(e)})
    
    async def _browse_recursive(self, node: Node, results: List[BrowseResult], max_depth: int, current_depth: int):
        """Recursively browse nodes"""
        if current_depth >= max_depth:
            return
            
        try:
            # Browse children
            children = await node.get_children()
            
            for child in children:
                try:
                    # Get node attributes
                    browse_name = await child.read_browse_name()
                    node_class = await child.read_node_class()
                    
                    # Check if it's a folder
                    is_folder = node_class == ua.NodeClass.Object
                    
                    # Create browse result
                    browse_result = BrowseResult(
                        node_id=str(child.nodeid),
                        name=browse_name.Name,
                        node_class=str(node_class),
                        is_folder=is_folder
                    )
                    
                    results.append(browse_result)
                    
                    # Recursively browse folders
                    if is_folder and current_depth < max_depth - 1:
                        await self._browse_recursive(child, browse_result.children, max_depth, current_depth + 1)
                        
                except Exception as e:
                    logger.warning(f"Failed to browse child node: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Failed to browse node {node}: {e}")
    
    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test connection health"""
        try:
            if not self._connected:
                return False, "Not connected"
                
            # Try to read the test node
            if self._test_node_id:
                try:
                    await self._client.get_node(self._test_node_id).read_value()
                    return True, None
                except ua.UaError as ua_error:
                    if "BadAttributeIdInvalid" in str(ua_error):
                        # Node exists but doesn't have a value - that's OK for health check
                        return True, None
                    else:
                        return False, f"UA Error: {ua_error}"
            else:
                # No test node configured - just check if connected
                return self._connected, None
            
        except Exception as e:
            return False, str(e) 