"""
Binalyze AIR Python SDK

A comprehensive Python SDK for interacting with the Binalyze AIR API with modern features:
- Filter Builder with fluent interface
- Constants and enums for all modules
- Verbose and debug logging with HTTP tracing
- Environment variable/.env file configuration support
- Versioning for AIR compatibility
- Future-proofed package structure
"""

# Main SDK interface
from .sdk import (
    SDK, 
    create_sdk, 
    create_sdk_from_env, 
    create_sdk_with_debug, 
    create_sdk_with_verbose,
    get_sdk,
    set_default_sdk,
    __version__ as sdk_version,
    __air_version__ as air_version,
    __supported_air_versions__ as supported_air_versions
)

# Filter builder
from .filter_builder import (
    FilterBuilder,
    filter_builder,
    assets as _filter_assets_impl,
    tasks as _filter_tasks_impl,
    cases as _filter_cases_impl,
    asset_tasks as _filter_asset_tasks_impl,
    acquisitions as _filter_acquisitions_impl,
    AssetFilterBuilder,
    TaskFilterBuilder,
    CaseFilterBuilder,
    AssetTaskFilterBuilder,
    AcquisitionFilterBuilder
)

# Create properly typed aliases that preserve return types
def filter_assets() -> AssetFilterBuilder:
    """Create a new asset filter builder."""
    return _filter_assets_impl()

def filter_tasks() -> TaskFilterBuilder:
    """Create a new task filter builder."""
    return _filter_tasks_impl()

def filter_cases() -> CaseFilterBuilder:
    """Create a new case filter builder."""
    return _filter_cases_impl()

def filter_asset_tasks() -> AssetTaskFilterBuilder:
    """Create a new asset task filter builder."""
    return _filter_asset_tasks_impl()

def filter_acquisitions() -> AcquisitionFilterBuilder:
    """Create a new acquisition filter builder."""
    return _filter_acquisitions_impl()

# Constants - re-export all for easy access
from .constants import (
    # Status and States
    AssetStatus, AssetPlatform, AssetManagedStatus, AssetIsolationStatus, AssetIssueType,
    TaskStatus, TaskType, TaskExecutionType,
    CaseStatus, CasePriority,
    AcquisitionType, AcquisitionStatus,
    OrganizationRole, OrganizationStatus,
    RepositoryType, AuditLevel, AuditEventType,
    TriageRuleType, TriageRuleSeverity,
    FilterOperator, FilterLogic,
    WebhookEventType, LicenseType, CloudProvider,
    NotificationType, NotificationStatus,
    PolicyType, PolicyStatus,
    EventSubscriptionType, UploadStatus,
    LogLevel, Defaults, Validation, ErrorMessages, FieldMappings,
    ALL_CONSTANTS
)

# Logging utilities
from .logging import (
    configure_logging,
    enable_verbose_logging,
    enable_debug_logging,
    disable_logging,
    get_logger,
    performance_timer
)

# Environment configuration
from .env_config import (
    EnvConfig,
    load_env_config,
    create_sample_env_file
)

# Legacy client for backwards compatibility
from .client import AIRClient
from .config import AIRConfig

# Common models for direct access
from .models import (
    # Assets
    Asset, AssetDetail, AssetTask, AssetFilter, AssetTaskFilter,
    # Cases
    Case, CaseActivity, CaseEndpoint, CaseTask, User, CaseFilter, CaseActivityFilter,
    CreateCaseRequest, UpdateCaseRequest, CaseStatus as CaseStatusModel,
    # Tasks
    Task, TaskFilter, TaskStatus as TaskStatusModel, TaskType as TaskTypeModel,
    # Acquisitions
    AcquisitionProfile, AcquisitionProfileDetails, AcquisitionFilter,
    AcquisitionTaskRequest, ImageAcquisitionTaskRequest, CreateAcquisitionProfileRequest,
    # Audit
    AuditLog, AuditFilter, AuditLogsFilter, AuditSummary, AuditUserActivity, AuditSystemEvent,
)

# Exceptions
from .exceptions import (
    AIRAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

__version__ = sdk_version
__all__ = [
    # Main SDK interface
    "SDK",
    "create_sdk",
    "create_sdk_from_env", 
    "create_sdk_with_debug",
    "create_sdk_with_verbose",
    "get_sdk",
    "set_default_sdk",
    
    # Filter builder
    "FilterBuilder",
    "filter_builder",
    "filter_assets",
    "filter_tasks", 
    "filter_cases",
    "filter_asset_tasks",
    "filter_acquisitions",
    
    # Constants - Status and States
    "AssetStatus", "AssetPlatform", "AssetManagedStatus", "AssetIsolationStatus", "AssetIssueType",
    "TaskStatus", "TaskType", "TaskExecutionType",
    "CaseStatus", "CasePriority",
    "AcquisitionType", "AcquisitionStatus",
    "OrganizationRole", "OrganizationStatus",
    "RepositoryType", "AuditLevel", "AuditEventType",
    "TriageRuleType", "TriageRuleSeverity",
    "FilterOperator", "FilterLogic",
    "WebhookEventType", "LicenseType", "CloudProvider",
    "NotificationType", "NotificationStatus",
    "PolicyType", "PolicyStatus",
    "EventSubscriptionType", "UploadStatus",
    "LogLevel", "Defaults", "Validation", "ErrorMessages", "FieldMappings",
    "ALL_CONSTANTS",
    
    # Logging
    "configure_logging",
    "enable_verbose_logging",
    "enable_debug_logging",
    "disable_logging",
    "get_logger",
    "performance_timer",
    
    # Environment configuration
    "EnvConfig",
    "load_env_config",
    "create_sample_env_file",
    
    # Legacy compatibility
    "AIRClient",
    "AIRConfig",
    
    # Common models
    "Asset", "AssetDetail", "AssetTask", "AssetFilter", "AssetTaskFilter",
    "Case", "CaseActivity", "CaseEndpoint", "CaseTask", "User", "CaseFilter", "CaseActivityFilter",
    "CreateCaseRequest", "UpdateCaseRequest", "CaseStatusModel",
    "Task", "TaskFilter", "TaskStatusModel", "TaskTypeModel",
    "AcquisitionProfile", "AcquisitionProfileDetails", "AcquisitionFilter",
    "AcquisitionTaskRequest", "ImageAcquisitionTaskRequest", "CreateAcquisitionProfileRequest",
    "AuditLog", "AuditFilter", "AuditLogsFilter", "AuditSummary", "AuditUserActivity", "AuditSystemEvent",
    
    # Exceptions
    "AIRAPIError",
    "AuthenticationError",
    "NotFoundError", 
    "ValidationError",
    "RateLimitError",
]

# Create a default SDK instance that can be configured later
sdk = None

# Usage examples in docstring
"""
Examples:
    # Modern SDK usage:
    from binalyze.air import sdk

    # Create SDK instance with .env file
    my_sdk = create_sdk_from_env('.env')
    
    # Create SDK instance with parameters 
    my_sdk = create_sdk(
        host="https://your-air-instance.com",
        api_token="your-token",
        organization_id=0
    )
    
    # Use filter builder (as requested)
    builder = my_sdk.filter
    asset_filter = builder.asset().add_included_endpoints(['endpoint1']).add_organization(0).build()
    
    # Alternative filter syntax
    from binalyze.air import filter_assets, AssetStatus
    asset_filter = filter_assets().is_online().platform([AssetPlatform.WINDOWS]).build()
    
    # Get assets with filter
    assets = my_sdk.assets.get_assets(filter=asset_filter)
    
    # Use constants
    from binalyze.air import AssetStatus, TaskType, CaseStatus
    print(f"Asset is {AssetStatus.ONLINE}")
    
    # Enable debugging
    my_sdk.enable_debug_logging()
    
    # Legacy compatibility:
    from binalyze.air import AIRClient, AIRConfig
    client = AIRClient(AIRConfig.create(host="...", api_token="...", organization_id=0))
"""
