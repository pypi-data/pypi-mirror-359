# Binalyze AIR Python SDK

A comprehensive Python SDK for interacting with the Binalyze AIR API.

## Installation

```bash
pip install binalyze
```

## Quick Start

```python
from binalyze.air import create_sdk, filter_assets, AssetPlatform

# Create SDK instance
sdk = create_sdk(
    host="https://your-air-instance.com",
    api_token="your-api-token",
    organization_id=0
)

# Use filter builder
asset_filter = filter_assets().is_online().platform([AssetPlatform.WINDOWS]).build()
assets = sdk.assets.get_assets(filter=asset_filter)
```

## Environment Configuration

Create a `.env` file for easy configuration:

```env
AIR_HOST=https://your-air-instance.com
AIR_API_TOKEN=your-api-token-here
AIR_ORGANIZATION_ID=0
```

Then use:

```python
from binalyze.air import create_sdk_from_env

sdk = create_sdk_from_env('.env')
```

## Filter Builder

Build complex filters with a fluent interface:

```python
from binalyze.air import filter_assets, AssetPlatform, AssetStatus

# Basic filtering
my_filter = (filter_assets()
             .add_organization(0)
             .add_included_endpoints(['endpoint-001', 'endpoint-002'])
             .platform([AssetPlatform.WINDOWS, AssetPlatform.LINUX])
             .is_online()
             .tags(['production', 'critical'])
             .build())

assets = sdk.assets.get_assets(filter=my_filter)
```

## Available Constants

Use built-in constants instead of string values:

```python
from binalyze.air import AssetPlatform, TaskStatus, CaseStatus

AssetPlatform.WINDOWS    # 'windows'
AssetPlatform.LINUX      # 'linux'
TaskStatus.COMPLETED     # 'completed'
CaseStatus.OPEN          # 'open'
```

## Logging

Enable verbose or debug logging:

```python
from binalyze.air import create_sdk_with_verbose, create_sdk_with_debug

# Verbose logging
sdk = create_sdk_with_verbose(host="...", api_token="...", organization_id=0)

# Debug logging with HTTP traces
sdk = create_sdk_with_debug(host="...", api_token="...", organization_id=0)
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `simple_filter_example.py` - Basic filter usage patterns
- `filter_examples.py` - Comprehensive filter demonstrations
- `real_world_example.py` - Production-ready examples
- `interactive_discovery.py` - How to discover available options

## Package Structure

```
binalyze/
└── air/
    ├── sdk.py              # Main SDK interface
    ├── filter_builder.py   # Filter builder system
    ├── constants.py        # All constants and enums
    ├── logging.py          # Logging utilities
    ├── env_config.py       # Environment configuration
    ├── client.py           # Legacy client (backward compatibility)
    ├── models/             # Data models
    ├── apis/               # API interfaces
    └── commands/           # Command implementations
```

## Backward Compatibility

The SDK maintains full backward compatibility with the previous `binalyze-air-sdk` package:

```python
# Legacy usage still works
from binalyze.air import AIRClient, AIRConfig

client = AIRClient(AIRConfig.create(
    host="https://your-air-instance.com",
    api_token="your-token",
    organization_id=0
))
```

## Features

- Fluent interface filter builder with method chaining
- 35+ filter methods with full IDE autocomplete support
- 35 constant categories covering all API values
- Environment variable configuration with .env file support
- Comprehensive logging with HTTP request/response tracing
- Type hints and full IDE support
- Backward compatibility with existing code
- Future-proof package structure

## Requirements

- Python 3.7+
- requests
- pydantic v2
- python-dotenv (optional, for .env file support)

## License

See LICENSE file for details.

## Support

For issues and questions, please refer to the official Binalyze documentation or contact support. 