"""
DataSources Library - Unified interface for industrial data sources

A simple, extensible library for connecting to industrial data sources
like OPC-UA, Modbus, and more.
"""

__version__ = "0.1.0"
__author__ = "Your Team"

# Base classes
from .base import (
    BaseDataSource,
    NodeValue,
    ConnectionStatus,
    BrowseResult,
)

# Configuration
from .config import (
    DataSourceType,
    BaseConfig,
    OpcUaConfig,
    ModbusConfig,
    DataSourcesConfig,
    load_config_from_toml,
)

# Connection pool
from .pool import ConnectionPool

# Exceptions
from .exceptions import (
    DataSourceError,
    ConnectionError,
    ConfigurationError,
    ReadError,
    WriteError,
    TimeoutError,
)

# OPC-UA implementation
from .opcua.client import OpcUaClient

__all__ = [
    # Version
    "__version__",
    
    # Base classes
    "BaseDataSource",
    "NodeValue",
    "ConnectionStatus",
    "BrowseResult",
    
    # Configuration
    "DataSourceType",
    "BaseConfig",
    "OpcUaConfig",
    "ModbusConfig",
    "DataSourcesConfig",
    "load_config_from_toml",
    
    # Pool
    "ConnectionPool",
    
    # Exceptions
    "DataSourceError",
    "ConnectionError", 
    "ConfigurationError",
    "ReadError",
    "WriteError",
    "TimeoutError",
    
    # Implementations
    "OpcUaClient",
]

# Configure logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())