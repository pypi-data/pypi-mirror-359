"""
Constants and enums for the Binalyze AIR SDK.
"""

from enum import Enum
from typing import List, Dict, Any


# Global Constants
class APIVersion:
    """Supported AIR API versions."""
    V1 = "v1"
    LATEST = "v1"


class ResponseStatus:
    """Standard API response status codes."""
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500


# Asset Constants
class AssetStatus:
    """Asset status constants."""
    ONLINE = "online"
    OFFLINE = "offline"


class AssetPlatform:
    """Asset platform constants."""
    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"
    AIX = "aix"
    DISK_IMAGE = "disk-image"


class AssetManagedStatus:
    """Asset managed status constants."""
    MANAGED = "managed"
    UNMANAGED = "unmanaged"
    OFF_NETWORK = "off-network"


class AssetIsolationStatus:
    """Asset isolation status constants."""
    ISOLATING = "isolating"
    ISOLATED = "isolated"
    UNISOLATING = "unisolating"
    UNISOLATED = "unisolated"


class AssetIssueType:
    """Asset issue type constants."""
    UNREACHABLE = "unreachable"
    OLD_VERSION = "old-version"
    UPDATE_REQUIRED = "update-required"


# Task Constants
class TaskStatus:
    """Task status constants."""
    SCHEDULED = "scheduled"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    COMPRESSING = "compressing"
    UPLOADING = "uploading"
    ANALYZING = "analyzing"
    PARTIALLY_COMPLETED = "partially-completed"


class TaskType:
    """Task type constants."""
    ACQUISITION = "acquisition"
    OFFLINE_ACQUISITION = "offline-acquisition"
    TRIAGE = "triage"
    OFFLINE_TRIAGE = "offline-triage"
    INVESTIGATION = "investigation"
    INTERACT_SHELL = "interact-shell"
    BASELINE_COMPARISON = "baseline-comparison"
    BASELINE_ACQUISITION = "baseline-acquisition"
    ACQUIRE_IMAGE = "acquire-image"
    REBOOT = "reboot"
    SHUTDOWN = "shutdown"
    ISOLATION = "isolation"
    LOG_RETRIEVAL = "log-retrieval"
    VERSION_UPDATE = "version-update"


class TaskExecutionType:
    """Task execution type constants."""
    INSTANT = "instant"
    SCHEDULED = "scheduled"


# Case Constants
class CaseStatus:
    """Case status constants."""
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CasePriority:
    """Case priority constants."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Acquisition Constants
class AcquisitionType:
    """Acquisition type constants."""
    EVIDENCE = "evidence"
    IMAGE = "image"
    BASELINE = "baseline"


class AcquisitionStatus:
    """Acquisition status constants."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Organization Constants
class OrganizationRole:
    """Organization role constants."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class OrganizationStatus:
    """Organization status constants."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# Repository Constants
class RepositoryType:
    """Repository type constants."""
    LOCAL = "local"
    SMB = "smb"
    SFTP = "sftp"
    FTPS = "ftps"
    AMAZON_S3 = "amazon-s3"
    AZURE_STORAGE = "azure-storage"
    GOOGLE_CLOUD = "google-cloud"


# Audit Constants
class AuditLevel:
    """Audit level constants."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEventType:
    """Audit event type constants."""
    USER_LOGIN = "user-login"
    USER_LOGOUT = "user-logout"
    TASK_CREATED = "task-created"
    TASK_COMPLETED = "task-completed"
    CASE_CREATED = "case-created"
    CASE_UPDATED = "case-updated"
    ASSET_REGISTERED = "asset-registered"
    ASSET_UNREGISTERED = "asset-unregistered"


# Triage Constants
class TriageRuleType:
    """Triage rule type constants."""
    YARA = "yara"
    SIGMA = "sigma"
    OSQUERY = "osquery"
    CUSTOM = "custom"


class TriageRuleSeverity:
    """Triage rule severity constants."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Filter Constants
class FilterOperator:
    """Filter operator constants."""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class FilterLogic:
    """Filter logic constants."""
    AND = "and"
    OR = "or"
    NOT = "not"


# Webhook Constants
class WebhookEventType:
    """Webhook event type constants."""
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    CASE_CREATED = "case.created"
    CASE_UPDATED = "case.updated"
    ASSET_ONLINE = "asset.online"
    ASSET_OFFLINE = "asset.offline"
    ALERT_CREATED = "alert.created"


# License Constants
class LicenseType:
    """License type constants."""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"


# Cloud Provider Constants
class CloudProvider:
    """Cloud provider constants."""
    AWS = "aws"
    AZURE = "azure"
    GOOGLE_CLOUD = "google-cloud"
    ALIBABA_CLOUD = "alibaba-cloud"


# Notification Constants
class NotificationType:
    """Notification type constants."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class NotificationStatus:
    """Notification status constants."""
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"


# Policy Constants
class PolicyType:
    """Policy type constants."""
    ACQUISITION = "acquisition"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    RETENTION = "retention"


class PolicyStatus:
    """Policy status constants."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


# Event Subscription Constants
class EventSubscriptionType:
    """Event subscription type constants."""
    WEBHOOK = "webhook"
    EMAIL = "email"
    SYSLOG = "syslog"
    SPLUNK = "splunk"


# Multipart Upload Constants
class UploadStatus:
    """Upload status constants."""
    INITIALIZED = "initialized"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Logging Constants
class LogLevel:
    """Logging level constants."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Default Values
class Defaults:
    """Default values for various operations."""
    ORGANIZATION_ID = 0
    PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    TIMEOUT = 30
    RETRY_COUNT = 3
    RETRY_DELAY = 1.0


# Validation Constants
class Validation:
    """Validation constants."""
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    MIN_CASE_NAME_LENGTH = 1
    MAX_CASE_NAME_LENGTH = 100
    MIN_TAG_NAME_LENGTH = 1
    MAX_TAG_NAME_LENGTH = 50


# Error Messages
class ErrorMessages:
    """Standard error messages."""
    INVALID_CREDENTIALS = "Invalid credentials provided"
    UNAUTHORIZED_ACCESS = "Unauthorized access"
    RESOURCE_NOT_FOUND = "Resource not found"
    VALIDATION_FAILED = "Validation failed"
    SERVER_ERROR = "Internal server error"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
    TIMEOUT_ERROR = "Request timeout"
    CONNECTION_ERROR = "Connection error"
    INVALID_FILTER = "Invalid filter parameters"
    MISSING_REQUIRED_FIELD = "Missing required field"


# Field Mappings for API compatibility
class FieldMappings:
    """Field mappings for API compatibility."""
    SNAKE_TO_CAMEL = {
        "organization_id": "organizationId",
        "endpoint_id": "endpointId",
        "endpoint_ids": "endpointIds",
        "case_id": "caseId",
        "task_id": "taskId",
        "user_id": "userId",
        "group_id": "groupId",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
        "last_seen": "lastSeen",
        "ip_address": "ipAddress",
        "managed_status": "managedStatus",
        "isolation_status": "isolationStatus",
        "online_status": "onlineStatus",
        "group_full_path": "groupFullPath",
        "net_interfaces": "netInterfaces",
        "security_token": "securityToken",
        "version_no": "versionNo",
        "build_arch": "buildArch",
        "system_resources": "systemResources",
        "has_evidence": "hasEvidence",
        "relay_server_id": "relayServerId",
        "connection_route": "connectionRoute",
        "asset_id": "assetId",
        "asset_type": "assetType",
        "timezone_offset": "timezoneOffset",
        "vendor_id": "vendorId",
        "vendor_device_id": "vendorDeviceId",
        "responder_id": "responderId",
        "excluded_from_updates": "excludedFromUpdates",
        "unsupported_os_to_update": "unsupportedOsToUpdate",
        "version_updating": "versionUpdating",
        "waiting_for_version_update_fix": "waitingForVersionUpdateFix",
    }
    
    CAMEL_TO_SNAKE = {v: k for k, v in SNAKE_TO_CAMEL.items()}


# All constants for export
ALL_CONSTANTS = {
    # Status and States
    "ASSET_STATUS": AssetStatus,
    "ASSET_PLATFORM": AssetPlatform,
    "ASSET_MANAGED_STATUS": AssetManagedStatus,
    "ASSET_ISOLATION_STATUS": AssetIsolationStatus,
    "ASSET_ISSUE_TYPE": AssetIssueType,
    
    # Tasks
    "TASK_STATUS": TaskStatus,
    "TASK_TYPE": TaskType,
    "TASK_EXECUTION_TYPE": TaskExecutionType,
    
    # Cases
    "CASE_STATUS": CaseStatus,
    "CASE_PRIORITY": CasePriority,
    
    # Acquisitions
    "ACQUISITION_TYPE": AcquisitionType,
    "ACQUISITION_STATUS": AcquisitionStatus,
    
    # Organizations
    "ORGANIZATION_ROLE": OrganizationRole,
    "ORGANIZATION_STATUS": OrganizationStatus,
    
    # Other
    "REPOSITORY_TYPE": RepositoryType,
    "AUDIT_LEVEL": AuditLevel,
    "AUDIT_EVENT_TYPE": AuditEventType,
    "TRIAGE_RULE_TYPE": TriageRuleType,
    "TRIAGE_RULE_SEVERITY": TriageRuleSeverity,
    "FILTER_OPERATOR": FilterOperator,
    "FILTER_LOGIC": FilterLogic,
    "WEBHOOK_EVENT_TYPE": WebhookEventType,
    "LICENSE_TYPE": LicenseType,
    "CLOUD_PROVIDER": CloudProvider,
    "NOTIFICATION_TYPE": NotificationType,
    "NOTIFICATION_STATUS": NotificationStatus,
    "POLICY_TYPE": PolicyType,
    "POLICY_STATUS": PolicyStatus,
    "EVENT_SUBSCRIPTION_TYPE": EventSubscriptionType,
    "UPLOAD_STATUS": UploadStatus,
    "LOG_LEVEL": LogLevel,
    
    # Defaults and Validation
    "DEFAULTS": Defaults,
    "VALIDATION": Validation,
    "ERROR_MESSAGES": ErrorMessages,
    "FIELD_MAPPINGS": FieldMappings,
} 