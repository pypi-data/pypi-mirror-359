"""Base interface for all data source implementations"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum


class ConnectionStatus(Enum):
    """Connection status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class NodeValue:
    """Data class for node values"""
    node_id: str
    value: Any
    timestamp: Optional[datetime] = None
    status: Optional[str] = None
    quality: str = "GOOD"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "value": self.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status,
            "quality": self.quality
        }


@dataclass
class BrowseResult:
    """Result from browsing nodes"""
    node_id: str
    name: str
    node_class: str
    is_folder: bool = False
    children: List['BrowseResult'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class BaseDataSource(ABC):
    """Base class for all data source implementations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data source with configuration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._connected = False
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._connection_lock = asyncio.Lock()
        
    @property
    def connected(self) -> bool:
        """Check if connected"""
        return self._connected
    
    @property
    def connection_status(self) -> ConnectionStatus:
        """Get current connection status"""
        return self._connection_status
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the data source
        
        Returns:
            bool: True if connected successfully
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the data source
        
        Returns:
            bool: True if disconnected successfully
        """
        pass
    
    @abstractmethod
    async def read_node(self, node_id: str) -> Optional[NodeValue]:
        """
        Read a single node value
        
        Args:
            node_id: Node identifier
            
        Returns:
            NodeValue or None if error
        """
        pass
    
    @abstractmethod
    async def read_nodes(self, node_ids: List[str]) -> Dict[str, Optional[NodeValue]]:
        """
        Read multiple node values (bulk read)
        
        Args:
            node_ids: List of node identifiers
            
        Returns:
            Dict mapping node_id to NodeValue
        """
        pass
    
    @abstractmethod
    async def write_node(self, node_id: str, value: Any) -> bool:
        """
        Write value to a node
        
        Args:
            node_id: Node identifier
            value: Value to write
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    async def browse(self, start_node: Optional[str] = None, max_depth: int = 1) -> List[BrowseResult]:
        """
        Browse available nodes
        
        Args:
            start_node: Starting node (None for root)
            max_depth: Maximum depth to browse
            
        Returns:
            List of browse results
        """
        pass
    
    async def ensure_connected(self) -> bool:
        """Ensure connection is established"""
        if not self._connected:
            return await self.connect()
        return True
    
    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test connection health
        
        Returns:
            Tuple of (is_healthy, error_message)
        """
        try:
            # Default implementation - try to read a simple value
            if hasattr(self, '_test_node_id'):
                result = await self.read_node(self._test_node_id)
                return (result is not None, None)
            return (self._connected, None)
        except Exception as e:
            return (False, str(e))