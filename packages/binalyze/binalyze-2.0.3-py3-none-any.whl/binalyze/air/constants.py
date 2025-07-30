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


class UserRoleType:
    """User role type constants."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"


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
    """Comprehensive notification type constants."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    TASK_COMPLETED = "task-completed"
    TASK_FAILED = "task-failed"
    FLAG_CREATED = "flag-created"
    FLAG_UPDATED = "flag-updated"
    FLAG_DELETED = "flag-deleted"
    ASSET_CREATED = "asset-created"
    ASSET_REGISTERED = "asset-registered"
    ASSET_REGISTER_FAILED = "asset-register-failed"
    ASSET_RE_REGISTERED = "asset-re-registered"
    ASSET_RE_REGISTER_FAILED = "asset-re-register-failed"
    CASE_CREATED = "case-created"
    CASE_COMMENT_ADDED = "case-comment-added"
    POLICY_EXECUTED = "policy-executed"
    SYSTEM_UPDATE = "system-update"
    ALERT = "alert"
    UPDATE_CHECK_FAILED = "update-check-failed"
    NATS_PORT_DISABLED = "nats-port-disabled"
    LDAP_SYNC_AUTH_FAILED = "ldap-sync-auth-failed"
    CLOUD_SYNC_FAILED = "cloud-sync-failed"
    REMOTE_BACKUP_DELETION_FAILED = "remote-backup-deletion-failed"
    TASK_CANCELLED_AS_CASE_CLOSED = "task-cancelled-as-case-closed"
    FINDING_EXCLUSION_CREATED = "finding-exclusion-created"
    FINDING_EXCLUSION_UPDATED = "finding-exclusion-updated"
    FINDING_EXCLUSION_DELETED = "finding-exclusion-deleted"
    TASK_COMMENT_ADDED = "task-comment-added"
    NEW_VERSION_RELEASED = "new-version-released"
    UPDATE_SCHEDULED = "update-scheduled"
    UPDATE_COMPLETED = "update-completed"
    UPDATE_FAILED = "update-failed"


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


# Auto Asset Tags Constants
class AutoAssetTagConditionField:
    """Auto asset tag condition field constants."""
    HOSTNAME = "hostname"
    IP_ADDRESS = "ip-address"
    SUBNET = "subnet"
    OSQUERY = "osquery"
    PROCESS = "process"
    FILE = "file"
    DIRECTORY = "directory"


class AutoAssetTagConditionOperator:
    """Auto asset tag condition operator constants."""
    RUNNING = "running"
    EXIST = "exist"
    IS = "is"
    CONTAINS = "contains"
    STARTS_WITH = "starts-with"
    ENDS_WITH = "ends-with"
    IN_RANGE = "in-range"
    HAS_RESULT = "has-result"
    NOT_RUNNING = "not-running"
    NOT_EXIST = "not-exist"
    HAS_NO_RESULT = "has-no-result"


class AutoAssetTagLogicalOperator:
    """Auto asset tag logical operator constants."""
    AND = "and"
    OR = "or"


# Notification Constants (Enhanced)
class NotificationLevel:
    """Notification level constants."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


# Interact Constants
class InteractSendToLocation:
    """Interact send to location constants."""
    USER_LOCAL = "user-local"
    REPOSITORY = "repository"
    EVIDENCE_REPOSITORY = "evidence-repository"


class InteractTaskConfigChoice:
    """Interact task configuration choice constants."""
    USE_POLICY = "use-policy"
    USE_CUSTOM_OPTIONS = "use-custom-options"


class InteractionType:
    """Interaction type constants."""
    SHELL = "shell"
    POWERSHELL = "powershell"
    CMD = "cmd"
    BASH = "bash"


class InteractionStatus:
    """Interaction status constants."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


# Backup Constants
class BackupStatus:
    """Backup status constants."""
    IN_PROGRESS = "in-progress"
    SUCCEEDED = "succeeded"
    UPLOADING = "uploading"
    FAILED = "failed"
    QUEUED = "queued"


class BackupSource:
    """Backup source constants."""
    USER = "user"
    SCHEDULER = "scheduler"


class BackupLocation:
    """Backup location constants."""
    LOCAL = "local"
    SFTP = "sftp"
    S3 = "s3"


# Cloud Forensics Constants
class CloudVendor:
    """Cloud vendor constants."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CloudAccountStatus:
    """Cloud account status constants."""
    CONFIGURED = "configured"
    SYNCING = "syncing"
    FAILED = "failed"


# Event Subscription Constants (Enhanced)
class SubscriptionStatus:
    """Event subscription status constants."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    FAILED = "failed"


class EventType:
    """Event type constants."""
    DEPLOYMENT_TOKEN_REGENERATED = "DeploymentTokenRegeneratedEvent"
    TASK_PROCESSING_FAILED = "TaskProcessingFailedEvent"
    TASK_PROCESSING_COMPLETED = "TaskProcessingCompletedEvent"
    CASE_FILE_SAVED = "CaseFileSavedEvent"
    TASK_FAILED = "TaskFailedEvent"
    ENDPOINT_ONLINE = "EndpointOnlineEvent"
    ENDPOINT_OFFLINE = "EndpointOfflineEvent"
    TASK_COMPLETED = "TaskCompletedEvent"
    ASSET_CREATED = "AssetCreatedEvent"
    ASSET_UPDATED = "AssetUpdatedEvent"
    ASSET_DELETED = "AssetDeletedEvent"
    CASE_CREATED = "CaseCreatedEvent"
    CASE_UPDATED = "CaseUpdatedEvent"
    CASE_CLOSED = "CaseClosedEvent"
    TASK_STARTED = "TaskStartedEvent"
    POLICY_EXECUTED = "PolicyExecutedEvent"
    ALERT_TRIGGERED = "AlertTriggeredEvent"


class DeliveryMethod:
    """Event delivery method constants."""
    WEBHOOK = "webhook"
    EMAIL = "email"
    SYSLOG = "syslog"


# Baseline Constants
class BaselineStatus:
    """Baseline status constants."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CREATING = "creating"
    FAILED = "failed"


class BaselineType:
    """Baseline type constants."""
    SYSTEM = "system"
    SECURITY = "security"
    CUSTOM = "custom"
    COMPLIANCE = "compliance"


class ComparisonStatus:
    """Baseline comparison status constants."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ChangeType:
    """Baseline change type constants."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"


# Settings Constants
class BannerType:
    """Banner type constants."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    MAINTENANCE = "maintenance"


class BannerPosition:
    """Banner position constants."""
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"


class ProxyCertType:
    """Proxy certificate type constants."""
    PEM = "PEM"
    DER = "DER"
    PKCS12 = "PKCS12"


# Triage Constants (Enhanced)
class TriageStatus:
    """Triage status constants."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CREATING = "creating"
    FAILED = "failed"


class TriageSeverity:
    """Triage severity constants."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Audit Constants (Enhanced)
class AuditCategory:
    """Audit category constants."""
    SYSTEM = "system"
    SECURITY = "security"
    USER = "user"
    DATA = "data"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CASE_MANAGEMENT = "case_management"
    TASK_MANAGEMENT = "task_management"
    ASSET_MANAGEMENT = "asset_management"


class AuditAction:
    """Audit action constants."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXECUTE = "execute"
    EXPORT = "export"
    IMPORT = "import"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    APPROVE = "approve"
    REJECT = "reject"
    ASSIGN = "assign"
    UNASSIGN = "unassign"
    START = "start"
    STOP = "stop"
    CANCEL = "cancel"
    COMPLETE = "complete"


# Params Constants
class ArtifactType:
    """Artifact type constants."""
    FILE = "file"
    REGISTRY = "registry"
    PROCESS = "process"
    NETWORK = "network"
    MEMORY = "memory"
    DISK = "disk"
    LOG = "log"
    DATABASE = "database"
    BROWSER = "browser"
    EMAIL = "email"
    DOCUMENT = "document"
    IMAGE = "image"


class ArtifactCategory:
    """Artifact category constants."""
    SYSTEM = "system"
    SECURITY = "security"
    USER = "user"
    APPLICATION = "application"
    NETWORK = "network"
    FORENSIC = "forensic"
    MALWARE = "malware"
    COMMUNICATION = "communication"
    BROWSER = "browser"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"


class ParamsPlatform:
    """Platform constants from params module (includes both darwin and macos)."""
    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"
    MACOS = "macos"


# All constants for export
ALL_CONSTANTS = {
    # Global Constants
    "API_VERSION": APIVersion,
    "RESPONSE_STATUS": ResponseStatus,
    
    # Asset Constants
    "ASSET_STATUS": AssetStatus,
    "ASSET_PLATFORM": AssetPlatform,
    "ASSET_MANAGED_STATUS": AssetManagedStatus,
    "ASSET_ISOLATION_STATUS": AssetIsolationStatus,
    "ASSET_ISSUE_TYPE": AssetIssueType,
    
    # Task Constants
    "TASK_STATUS": TaskStatus,
    "TASK_TYPE": TaskType,
    "TASK_EXECUTION_TYPE": TaskExecutionType,
    
    # Case Constants
    "CASE_STATUS": CaseStatus,
    "CASE_PRIORITY": CasePriority,
    
    # Acquisition Constants
    "ACQUISITION_TYPE": AcquisitionType,
    "ACQUISITION_STATUS": AcquisitionStatus,
    
    # Organization Constants
    "ORGANIZATION_ROLE": OrganizationRole,
    "ORGANIZATION_STATUS": OrganizationStatus,
    "USER_ROLE_TYPE": UserRoleType,
    
    # Repository Constants
    "REPOSITORY_TYPE": RepositoryType,
    
    # Audit Constants
    "AUDIT_LEVEL": AuditLevel,
    "AUDIT_EVENT_TYPE": AuditEventType,
    "AUDIT_CATEGORY": AuditCategory,
    "AUDIT_ACTION": AuditAction,
    
    # Triage Constants
    "TRIAGE_RULE_TYPE": TriageRuleType,
    "TRIAGE_RULE_SEVERITY": TriageRuleSeverity,
    "TRIAGE_STATUS": TriageStatus,
    "TRIAGE_SEVERITY": TriageSeverity,
    
    # Filter Constants
    "FILTER_OPERATOR": FilterOperator,
    "FILTER_LOGIC": FilterLogic,
    
    # Webhook Constants
    "WEBHOOK_EVENT_TYPE": WebhookEventType,
    
    # License Constants
    "LICENSE_TYPE": LicenseType,
    
    # Cloud Constants
    "CLOUD_PROVIDER": CloudProvider,
    "CLOUD_VENDOR": CloudVendor,
    "CLOUD_ACCOUNT_STATUS": CloudAccountStatus,
    
    # Notification Constants
    "NOTIFICATION_TYPE": NotificationType,
    "NOTIFICATION_STATUS": NotificationStatus,
    "NOTIFICATION_LEVEL": NotificationLevel,
    
    # Policy Constants
    "POLICY_TYPE": PolicyType,
    "POLICY_STATUS": PolicyStatus,
    
    # Event Subscription Constants
    "EVENT_SUBSCRIPTION_TYPE": EventSubscriptionType,
    "SUBSCRIPTION_STATUS": SubscriptionStatus,
    "EVENT_TYPE": EventType,
    "DELIVERY_METHOD": DeliveryMethod,
    
    # Upload Constants
    "UPLOAD_STATUS": UploadStatus,
    
    # Logging Constants
    "LOG_LEVEL": LogLevel,
    
    # Auto Asset Tag Constants
    "AUTO_ASSET_TAG_CONDITION_FIELD": AutoAssetTagConditionField,
    "AUTO_ASSET_TAG_CONDITION_OPERATOR": AutoAssetTagConditionOperator,
    "AUTO_ASSET_TAG_LOGICAL_OPERATOR": AutoAssetTagLogicalOperator,
    
    # Interact Constants
    "INTERACT_SEND_TO_LOCATION": InteractSendToLocation,
    "INTERACT_TASK_CONFIG_CHOICE": InteractTaskConfigChoice,
    "INTERACTION_TYPE": InteractionType,
    "INTERACTION_STATUS": InteractionStatus,
    
    # Backup Constants
    "BACKUP_STATUS": BackupStatus,
    "BACKUP_SOURCE": BackupSource,
    "BACKUP_LOCATION": BackupLocation,
    
    # Baseline Constants
    "BASELINE_STATUS": BaselineStatus,
    "BASELINE_TYPE": BaselineType,
    "COMPARISON_STATUS": ComparisonStatus,
    "CHANGE_TYPE": ChangeType,
    
    # Settings Constants
    "BANNER_TYPE": BannerType,
    "BANNER_POSITION": BannerPosition,
    "PROXY_CERT_TYPE": ProxyCertType,
    
    # Params Constants
    "ARTIFACT_TYPE": ArtifactType,
    "ARTIFACT_CATEGORY": ArtifactCategory,
    "PARAMS_PLATFORM": ParamsPlatform,
    
    # Utility Constants
    "DEFAULTS": Defaults,
    "VALIDATION": Validation,
    "ERROR_MESSAGES": ErrorMessages,
    "FIELD_MAPPINGS": FieldMappings,
} 