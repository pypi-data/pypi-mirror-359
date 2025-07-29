"""Custom exceptions for the DataSources library"""

from typing import Any, Dict, Optional


class DataSourceError(Exception):
    """Base exception for all data source errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConnectionError(DataSourceError):
    """Raised when connection to data source fails"""
    pass


class ConfigurationError(DataSourceError):
    """Raised when configuration is invalid"""
    pass


class ReadError(DataSourceError):
    """Raised when reading from data source fails"""
    
    def __init__(self, message: str, node_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.node_id = node_id


class WriteError(DataSourceError):
    """Raised when writing to data source fails"""
    
    def __init__(self, message: str, node_id: Optional[str] = None, value: Optional[Any] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.node_id = node_id
        self.value = value


class TimeoutError(DataSourceError):
    """Raised when operation times out"""
    
    def __init__(self, message: str, operation: Optional[str] = None, timeout: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.operation = operation
        self.timeout = timeout


class AuthenticationError(DataSourceError):
    """Raised when authentication fails"""
    pass


class BrowseError(DataSourceError):
    """Raised when browsing nodes fails"""
    
    def __init__(self, message: str, start_node: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.start_node = start_node