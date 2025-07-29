"""Simple connection pool for data sources"""

import asyncio
from typing import Dict, Optional, Type, Any
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import logging

from .base import BaseDataSource
from .config import BaseConfig, DataSourceType, OpcUaConfig
from .opcua.client import OpcUaClient
from .exceptions import ConnectionError, ConfigurationError

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Simple connection pool for managing data source connections"""
    
    # Registry of data source implementations
    _implementations: Dict[DataSourceType, Type[BaseDataSource]] = {
        DataSourceType.OPCUA: OpcUaClient,
    }
    
    def __init__(self, max_idle_time: int = 300):
        """
        Initialize connection pool
        
        Args:
            max_idle_time: Maximum idle time in seconds before closing connection
        """
        self._connections: Dict[str, BaseDataSource] = {}
        self._last_used: Dict[str, datetime] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._max_idle_time = timedelta(seconds=max_idle_time)
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the connection pool cleanup task"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Connection pool started")
    
    async def stop(self):
        """Stop the pool and close all connections"""
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for name in list(self._connections.keys()):
            await self.close_connection(name)
            
        logger.info("Connection pool stopped")
    
    @asynccontextmanager
    async def get_connection(self, config: BaseConfig):
        """
        Get a connection from the pool
        
        Args:
            config: Data source configuration
            
        Yields:
            BaseDataSource: Data source connection
        """
        name = config.name
        
        # Ensure lock exists
        if name not in self._locks:
            self._locks[name] = asyncio.Lock()
        
        async with self._locks[name]:
            # Get or create connection
            if name not in self._connections:
                datasource = await self._create_connection(config)
                self._connections[name] = datasource
            else:
                datasource = self._connections[name]
                
                # Test if connection is still alive
                is_healthy, error = await datasource.test_connection()
                if not is_healthy:
                    logger.warning(f"Connection {name} is unhealthy: {error}")
                    # Recreate connection
                    await datasource.disconnect()
                    datasource = await self._create_connection(config)
                    self._connections[name] = datasource
            
            # Update last used time
            self._last_used[name] = datetime.now()
        
        try:
            yield datasource
        finally:
            # Update last used time again
            self._last_used[name] = datetime.now()
    
    async def _create_connection(self, config: BaseConfig) -> BaseDataSource:
        """Create a new data source connection"""
        # Get implementation class
        impl_class = self._implementations.get(config.type)
        if not impl_class:
            raise ConfigurationError(
                f"Unsupported data source type: {config.type}",
                {"supported_types": list(self._implementations.keys())}
            )
        
        # Convert config to dict for client
        if isinstance(config, OpcUaConfig):
            client_config = config.to_client_config()
        else:
            client_config = config.model_dump()
        
        # Create and connect
        datasource = impl_class(client_config)
        success = await datasource.connect()
        
        if not success:
            raise ConnectionError(f"Failed to connect to {config.name}")
        
        logger.info(f"Created new connection: {config.name}")
        return datasource
    
    async def close_connection(self, name: str):
        """Close a specific connection"""
        if name in self._connections:
            try:
                await self._connections[name].disconnect()
            except Exception as e:
                logger.error(f"Error closing connection {name}: {e}")
            finally:
                del self._connections[name]
                if name in self._last_used:
                    del self._last_used[name]
                logger.info(f"Closed connection: {name}")
    
    async def _cleanup_loop(self):
        """Background task to clean up idle connections"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                now = datetime.now()
                to_close = []
                
                for name, last_used in self._last_used.items():
                    if now - last_used > self._max_idle_time:
                        to_close.append(name)
                
                for name in to_close:
                    logger.info(f"Closing idle connection: {name}")
                    await self.close_connection(name)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "active_connections": len(self._connections),
            "connections": {
                name: {
                    "connected": conn.connected,
                    "status": conn.connection_status.value,
                    "last_used": self._last_used.get(name, datetime.now()).isoformat()
                }
                for name, conn in self._connections.items()
            }
        }
    
    @classmethod
    def register_implementation(cls, data_type: DataSourceType, impl_class: Type[BaseDataSource]):
        """Register a new data source implementation"""
        cls._implementations[data_type] = impl_class
        logger.info(f"Registered implementation for {data_type}: {impl_class.__name__}")