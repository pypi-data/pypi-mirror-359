# Binalyze AIR Python SDK

A Python SDK for interacting with the Binalyze AIR API, providing type safety and comprehensive constants integration.

## Installation

```bash
pip install binalyze
```

## Quick Start

```python
from binalyze.air import create_sdk, filter_assets, AssetPlatform, AssetStatus

# Create SDK instance
sdk = create_sdk(
    host="https://your-air-instance.com",
    api_token="your-api-token",
    organization_id=0
)

# Use filter builder with constants
asset_filter = (filter_assets()
                .is_online()
                .platform([AssetPlatform.WINDOWS])
                .online_status([AssetStatus.ONLINE])
                .build())
assets = sdk.assets.get_assets(filter=asset_filter)
```

## Environment Configuration

Create a `.env` file for configuration:

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

## Constants

The SDK includes constants for API values:

```python
from binalyze.air import (
    AssetPlatform, AssetStatus, AssetManagedStatus,
    TaskStatus, TaskType, TaskExecutionType,
    CaseStatus, CasePriority, TriageSeverity
)

# Asset constants
AssetPlatform.WINDOWS           # 'windows'
AssetPlatform.LINUX            # 'linux'
AssetStatus.ONLINE             # 'online'
AssetManagedStatus.MANAGED     # 'managed'

# Task constants
TaskStatus.COMPLETED           # 'completed'
TaskType.ACQUISITION           # 'acquisition'
TaskExecutionType.INSTANT      # 'instant'

# Case constants
CaseStatus.OPEN               # 'open'
CasePriority.CRITICAL         # 'critical'

# Triage constants
TriageSeverity.HIGH           # 'high'
```

## Filter Builder

Build filters with a fluent interface:

```python
from binalyze.air import (
    filter_assets, filter_tasks, filter_cases,
    AssetPlatform, AssetStatus, AssetManagedStatus,
    TaskStatus, TaskType, TaskExecutionType, CasePriority
)

# Asset filtering
asset_filter = (filter_assets()
                .add_organization(0)
                .platform([AssetPlatform.WINDOWS, AssetPlatform.LINUX])
                .online_status([AssetStatus.ONLINE])
                .managed_status([AssetManagedStatus.MANAGED])
                .tags(['production', 'critical'])
                .build())

# Task filtering
task_filter = (filter_tasks()
               .status([TaskStatus.COMPLETED, TaskStatus.PROCESSING])
               .task_type([TaskType.ACQUISITION, TaskType.TRIAGE])
               .execution_type([TaskExecutionType.INSTANT])
               .build())

# Case filtering
case_filter = (filter_cases()
               .status([CaseStatus.OPEN])
               .priority([CasePriority.HIGH, CasePriority.CRITICAL])
               .build())
```

## Available Constants

The SDK provides constants for the following categories:

### Asset Management
- **AssetPlatform**: Windows, Linux, Darwin, AIX
- **AssetStatus**: Online, Offline  
- **AssetManagedStatus**: Managed, Unmanaged, Off-network
- **AssetIsolationStatus**: Isolated, Unisolated, Isolating, Unisolating

### Task Management
- **TaskStatus**: Scheduled, Processing, Completed, Failed, Cancelled
- **TaskType**: Acquisition, Triage, Investigation, Interact Shell
- **TaskExecutionType**: Instant, Scheduled

### Case Management
- **CaseStatus**: Open, Closed, Archived
- **CasePriority**: Low, Medium, High, Critical

### Security Operations
- **TriageStatus**: Active, Inactive, Creating, Failed
- **TriageSeverity**: Low, Medium, High, Critical
- **AuditLevel**: Info, Warning, Error, Critical

## Usage Examples

### Asset Management
```python
from binalyze.air import (
    create_sdk, filter_assets, filter_tasks,
    AssetPlatform, AssetStatus, TaskStatus, TaskType
)

sdk = create_sdk_from_env('.env')

# Find Windows assets that are online
critical_assets = (filter_assets()
                   .platform([AssetPlatform.WINDOWS])
                   .online_status([AssetStatus.ONLINE])
                   .tags(['critical'])
                   .build())

# Get acquisition tasks
recent_acquisitions = (filter_tasks()
                       .task_type([TaskType.ACQUISITION])
                       .status([TaskStatus.COMPLETED])
                       .build())

assets = sdk.assets.get_assets(filter=critical_assets)
tasks = sdk.tasks.get_tasks(filter=recent_acquisitions)
```

### Triage Operations
```python
from binalyze.air import TriageSeverity, TriageStatus

# Create triage rule
triage_data = {
    'name': 'High Priority Detection',
    'severity': TriageSeverity.HIGH,
    'status': TriageStatus.ACTIVE
}
```

## Logging

Configure logging levels:

```python
from binalyze.air import create_sdk_with_verbose, create_sdk_with_debug

# Verbose logging
sdk = create_sdk_with_verbose(host="...", api_token="...", organization_id=0)

# Debug logging with HTTP traces
sdk = create_sdk_with_debug(host="...", api_token="...", organization_id=0)
```

## Examples

The `examples/` directory contains usage examples:

- `01_basic_setup.py` - Basic SDK setup and configuration
- `02_assets.py` - Asset management operations
- `03_tasks.py` - Task operations
- `04_cases.py` - Case management
- `05_acquisitions.py` - Acquisition workflows
- `15_preset_filters.py` - Filter management
- `16_filter_builder.py` - Advanced filtering

## Package Structure

```
binalyze/
└── air/
    ├── sdk.py              # Main SDK interface
    ├── filter_builder.py   # Filter builder system
    ├── constants.py        # API constants
    ├── logging.py          # Logging utilities
    ├── env_config.py       # Environment configuration
    ├── client.py           # Legacy client compatibility
    ├── models/             # Data models
    ├── apis/               # API interfaces
    ├── commands/           # Command implementations
    └── queries/            # Query implementations
```

## Backward Compatibility

The SDK maintains compatibility with the previous `binalyze-air-sdk` package:

```python
# Legacy usage continues to work
from binalyze.air import AIRClient, AIRConfig

client = AIRClient(AIRConfig.create(
    host="https://your-air-instance.com",
    api_token="your-token",
    organization_id=0
))
```

## Features

- Constants integration for API values
- Fluent interface filter builder
- Environment variable configuration
- Comprehensive logging with HTTP tracing
- Type hints and IDE support
- Backward compatibility with existing code

## Requirements

- Python 3.7+
- requests
- pydantic v2
- python-dotenv (optional, for .env file support)

## License

See LICENSE file for details.

## Support

For issues and questions, please refer to the official Binalyze documentation or contact support. 