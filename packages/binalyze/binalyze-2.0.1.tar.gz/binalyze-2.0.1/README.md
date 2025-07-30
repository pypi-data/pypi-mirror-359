# Binalyze AIR Python SDK

A comprehensive Python SDK for interacting with the Binalyze AIR API with full constants integration and type safety.

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

## Constants Integration

The SDK now includes comprehensive constants for all API values, eliminating hardcoded strings:

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

Build complex filters with a fluent interface and constants:

```python
from binalyze.air import (
    filter_assets, filter_tasks, filter_cases,
    AssetPlatform, AssetStatus, AssetManagedStatus,
    TaskStatus, TaskType, TaskExecutionType, CasePriority
)

# Asset filtering with constants
asset_filter = (filter_assets()
                .add_organization(0)
                .platform([AssetPlatform.WINDOWS, AssetPlatform.LINUX])
                .online_status([AssetStatus.ONLINE])
                .managed_status([AssetManagedStatus.MANAGED])
                .tags(['production', CasePriority.CRITICAL])
                .build())

# Task filtering with constants
task_filter = (filter_tasks()
               .status([TaskStatus.COMPLETED, TaskStatus.PROCESSING])
               .task_type([TaskType.ACQUISITION, TaskType.TRIAGE])
               .execution_type([TaskExecutionType.INSTANT])
               .build())

# Case filtering with constants
case_filter = (filter_cases()
               .status([CaseStatus.OPEN])
               .priority([CasePriority.HIGH, CasePriority.CRITICAL])
               .build())
```

## Comprehensive Constants Coverage

The SDK includes 68+ constant categories covering all API domains:

### Core Constants
- **AssetPlatform**: Windows, Linux, Darwin, AIX
- **AssetStatus**: Online, Offline  
- **AssetManagedStatus**: Managed, Unmanaged, Off-network
- **AssetIsolationStatus**: Isolated, Unisolated, Isolating, Unisolating

### Task Constants
- **TaskStatus**: Scheduled, Processing, Completed, Failed, Cancelled
- **TaskType**: Acquisition, Triage, Investigation, Interact Shell
- **TaskExecutionType**: Instant, Scheduled

### Case Management
- **CaseStatus**: Open, Closed, Archived
- **CasePriority**: Low, Medium, High, Critical

### Triage & Security
- **TriageStatus**: Active, Inactive, Creating, Failed
- **TriageSeverity**: Low, Medium, High, Critical
- **AuditLevel**: Info, Warning, Error, Critical

### And many more covering all API endpoints and responses!

## Advanced Examples

### Real-world Production Example
```python
from binalyze.air import (
    create_sdk, filter_assets, filter_tasks,
    AssetPlatform, AssetStatus, TaskStatus, TaskType, CasePriority
)

sdk = create_sdk_from_env('.env')

# Find critical Windows assets that are online
critical_assets = (filter_assets()
                   .platform([AssetPlatform.WINDOWS])
                   .online_status([AssetStatus.ONLINE])
                   .tags([CasePriority.CRITICAL])
                   .build())

# Get recent acquisition tasks
recent_acquisitions = (filter_tasks()
                       .task_type([TaskType.ACQUISITION])
                       .status([TaskStatus.COMPLETED])
                       .build())

assets = sdk.assets.get_assets(filter=critical_assets)
tasks = sdk.tasks.get_tasks(filter=recent_acquisitions)
```

### Triage Example with Constants
```python
from binalyze.air import TriageSeverity, TriageStatus

# Create triage rule with constants
triage_data = {
    'name': 'High Priority Detection',
    'severity': TriageSeverity.HIGH,
    'status': TriageStatus.ACTIVE
}
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

## Examples Directory

See the `examples/` directory for comprehensive usage examples:

- `01_basic_setup.py` - Basic SDK setup and configuration
- `02_assets.py` - Asset management with constants
- `03_tasks.py` - Task operations with proper constants
- `04_cases.py` - Case management examples
- `05_acquisitions.py` - Acquisition workflows
- `15_preset_filters.py` - Filter management
- `16_filter_builder.py` - Advanced filtering patterns

## Package Structure

```
binalyze/
└── air/
    ├── sdk.py              # Main SDK interface
    ├── filter_builder.py   # Filter builder system (40+ filters)
    ├── constants.py        # 68+ constant categories (INTEGRATED!)
    ├── logging.py          # Logging utilities
    ├── env_config.py       # Environment configuration
    ├── client.py           # Legacy client (backward compatibility)
    ├── models/             # Data models (constants integrated)
    ├── apis/               # API interfaces (constants integrated) 
    ├── commands/           # Command implementations (constants integrated)
    └── queries/            # Query implementations (constants integrated)
```

## Constants Integration Status

**COMPLETED** - Full constants integration across entire codebase:
- **40+ files processed** with hardcoded strings replaced
- **68+ constant categories** covering all API domains
- **15+ atomic commits** with comprehensive coverage
- **100% backward compatibility** maintained
- **Zero breaking changes** introduced

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

## Key Features

- **Complete constants integration** - No more hardcoded strings!
- **Fluent interface filter builder** with method chaining
- **40+ filter methods** with full IDE autocomplete support
- **68+ constant categories** covering all API values
- **Environment variable configuration** with .env file support
- **Comprehensive logging** with HTTP request/response tracing
- **Type hints and full IDE support** with TypeVar method chaining
- **100% backward compatibility** with existing code
- **Future-proof package structure** and architecture

## Requirements

- Python 3.7+
- requests
- pydantic v2
- python-dotenv (optional, for .env file support)

## Recent Updates

### v2.0.0 - Constants Integration Complete
- Comprehensive constants integration across all 40+ files
- 68+ constant categories for all API domains
- Zero hardcoded strings remaining in business logic
- Full backward compatibility maintained
- Enhanced documentation with constant examples
- Improved type safety and IDE support

## License

See LICENSE file for details.

## Support

For issues and questions, please refer to the official Binalyze documentation or contact support. 