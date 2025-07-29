# DataSources Library

A unified Python library for connecting to industrial data sources with built-in connection pooling and async support.

## Features

- **Unified Interface**: Single API for multiple industrial protocols
- **Async-First**: Built with asyncio for high performance
- **Connection Pooling**: Efficient connection reuse and management
- **Type Safety**: Full type hints and Pydantic models
- **Production Ready**: Retry logic, error handling, and health monitoring
- **Extensible**: Easy to add new protocol implementations

## Supported Protocols

- ✅ **OPC-UA** - Fully implemented
- 🚧 **Modbus** - Planned
- 🚧 **MQTT** - Planned
- 🚧 **OPC-DA** - Planned

## Installation

```bash
pip install datasources-lib
```

## Quick Start

### Basic Usage

```python
import asyncio
from datasources_lib import OpcUaConfig, ConnectionPool

async def main():
    # Configuration
    config = OpcUaConfig(
        name="my_plc",
        type="opcua",
        url="opc.tcp://localhost:4840",
        username="admin",
        password="password"
    )
    
    # Connection pool
    pool = ConnectionPool()
    await pool.start()
    
    try:
        # Get connection
        async with pool.get_connection(config) as client:
            # Read a value
            value = await client.read_node("ns=2;s=Temperature")
            print(f"Temperature: {value.value}")
            
            # Write a value
            success = await client.write_node("ns=2;s=Setpoint", 25.0)
            print(f"Write successful: {success}")
            
    finally:
        await pool.stop()

asyncio.run(main())
```

### Configuration from TOML

```toml
# config.toml
[datasources]
default_source = "main_plc"

[datasources.sources.main_plc]
type = "opcua"
url = "opc.tcp://192.168.1.100:4840"
username = "admin"
password = "password"
max_retries = 3
retry_delay = 5.0
connection_timeout = 30.0

[datasources.sources.backup_plc]
type = "opcua"
url = "opc.tcp://192.168.1.101:4840"
username = "admin"
password = "password"
```

```python
import tomllib
from datasources_lib import load_config_from_toml, ConnectionPool

# Load configuration
with open("config.toml", "rb") as f:
    toml_data = tomllib.load(f)

config = load_config_from_toml(toml_data)
main_plc_config = config.get_source_config("main_plc")

# Use with connection pool
pool = ConnectionPool()
async with pool.get_connection(main_plc_config) as client:
    # Your code here
    pass
```

### Bulk Operations

```python
# Read multiple nodes at once
node_ids = ["ns=2;s=Temperature", "ns=2;s=Pressure", "ns=2;s=Flow"]
values = await client.read_nodes(node_ids)

for node_id, value in values.items():
    if value:
        print(f"{node_id}: {value.value}")
```

### Browsing Nodes

```python
# Browse available nodes
nodes = await client.browse(start_node="ns=2;s=MyDevice", max_depth=2)

for node in nodes:
    print(f"{node.node_id}: {node.name} ({node.node_class})")
    if node.is_folder:
        print(f"  Children: {len(node.children)}")
```

## Architecture

### Core Components

```
BaseDataSource (Abstract Interface)
    ├── OpcUaClient (Implemented)
    ├── ModbusClient (Future)
    └── MqttClient (Future)

ConnectionPool
    └── Manages multiple connections
    └── Auto-cleanup of idle connections
    └── Health monitoring
```

### Key Classes

- **BaseDataSource**: Abstract base class for all data sources
- **ConnectionPool**: Manages connection lifecycle and pooling
- **NodeValue**: Data class for node values with metadata
- **BrowseResult**: Data class for node browsing results

## Error Handling

The library provides comprehensive error handling with custom exceptions:

```python
from datasources_lib import (
    DataSourceError,
    ConnectionError,
    ReadError,
    WriteError,
    TimeoutError
)

try:
    value = await client.read_node("ns=2;s=Temperature")
except ReadError as e:
    print(f"Read failed: {e.message}")
    print(f"Node: {e.node_id}")
    print(f"Details: {e.details}")
except ConnectionError as e:
    print(f"Connection failed: {e.message}")
```

## Development

### Setup Development Environment

```bash
git clone <repository>
cd datasources-lib
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Roadmap

- [ ] Modbus TCP/RTU support
- [ ] MQTT support
- [ ] OPC-DA support
- [ ] Database connectors (PostgreSQL, InfluxDB)
- [ ] REST API connectors
- [ ] Subscription support for OPC-UA
- [ ] Data validation and transformation
- [ ] Metrics and monitoring
- [ ] Web UI for configuration management
