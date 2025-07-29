"""Configuration models for data sources"""

from typing import Any, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


class DataSourceType(str, Enum):
    """Supported data source types"""
    OPCUA = "opcua"
    OPCDA = "opcda"  # Future
    MODBUS = "modbus"  # Future
    MQTT = "mqtt"  # Future


class BaseConfig(BaseModel):
    """Base configuration for all data sources"""
    
    name: str = Field(..., description="Data source name")
    type: DataSourceType = Field(..., description="Data source type")
    enabled: bool = Field(True, description="Whether this data source is enabled")
    max_retries: int = Field(3, ge=0, description="Maximum connection retries")
    retry_delay: float = Field(5.0, gt=0, description="Delay between retries in seconds")
    connection_timeout: float = Field(30.0, gt=0, description="Connection timeout in seconds")
    
    class Config:
        use_enum_values = True
        extra = "allow"  # Allow extra fields for specific implementations


class OpcUaConfig(BaseConfig):
    """OPC-UA specific configuration"""
    
    url: str = Field(..., description="OPC-UA server URL")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[str] = Field(None, description="Password for authentication")
    security_policy: Optional[str] = Field(None, description="Security policy URI")
    security_mode: Optional[str] = Field("None", description="Security mode: None, Sign, SignAndEncrypt")
    test_node_id: Optional[str] = Field(None, description="Node ID to use for connection health checks")
    
    @validator("url")
    def validate_url(cls, v):
        """Validate OPC-UA URL format"""
        if not v.startswith(("opc.tcp://", "opc.https://", "opc.wss://")):
            raise ValueError("OPC-UA URL must start with opc.tcp://, opc.https://, or opc.wss://")
        return v
    
    @validator("security_mode")
    def validate_security_mode(cls, v):
        """Validate security mode"""
        valid_modes = ["None", "Sign", "SignAndEncrypt"]
        if v and v not in valid_modes:
            raise ValueError(f"Security mode must be one of: {', '.join(valid_modes)}")
        return v
    
    def to_client_config(self) -> Dict[str, Any]:
        """Convert to dictionary for client initialization"""
        return {
            "url": self.url,
            "username": self.username,
            "password": self.password,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "connection_timeout": self.connection_timeout,
            "test_node_id": self.test_node_id,
        }


class ModbusConfig(BaseConfig):
    """Modbus configuration (placeholder for future)"""
    
    host: str = Field(..., description="Modbus server host")
    port: int = Field(502, description="Modbus server port")
    unit_id: int = Field(1, ge=0, le=255, description="Modbus unit/slave ID")
    protocol: str = Field("tcp", description="Protocol: tcp or rtu")


class DataSourcesConfig(BaseModel):
    """Configuration for multiple data sources"""
    
    sources: Dict[str, BaseConfig] = Field(
        default_factory=dict,
        description="Dictionary of data source configurations"
    )
    default_source: Optional[str] = Field(None, description="Default data source name")
    
    @validator("default_source")
    def validate_default_source(cls, v, values):
        """Ensure default source exists in sources"""
        if v and "sources" in values and v not in values["sources"]:
            raise ValueError(f"Default source '{v}' not found in sources")
        return v
    
    def get_source_config(self, name: str) -> Optional[BaseConfig]:
        """Get configuration for a specific source"""
        return self.sources.get(name)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSourcesConfig":
        """Create from dictionary with proper type handling"""
        sources = {}
        
        for name, config in data.get("sources", {}).items():
            source_type = config.get("type", "").lower()
            
            if source_type == DataSourceType.OPCUA:
                sources[name] = OpcUaConfig(name=name, **config)
            elif source_type == DataSourceType.MODBUS:
                sources[name] = ModbusConfig(name=name, **config)
            else:
                # Default to base config for unknown types
                sources[name] = BaseConfig(name=name, **config)
        
        return cls(
            sources=sources,
            default_source=data.get("default_source")
        )


# Convenience function for loading from TOML
def load_config_from_toml(toml_data: Dict[str, Any]) -> DataSourcesConfig:
    """
    Load configuration from TOML data
    
    Expected TOML structure:
    [datasources]
    default_source = "main_plc"
    
    [datasources.sources.main_plc]
    type = "opcua"
    url = "opc.tcp://localhost:4840"
    username = "admin"
    password = "password"
    
    [datasources.sources.backup_plc]
    type = "opcua"
    url = "opc.tcp://192.168.1.100:4840"
    """
    datasources_section = toml_data.get("datasources", {})
    return DataSourcesConfig.from_dict(datasources_section)