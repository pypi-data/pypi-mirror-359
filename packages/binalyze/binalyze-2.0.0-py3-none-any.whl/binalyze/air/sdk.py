"""
Main SDK interface for Binalyze AIR.

Provides the primary entry point with all new features:
- Filter Builder
- Constants
- Verbose/Debug Logging
- .env Configuration Support
- Versioning
"""

import os
from typing import Optional, Union, Dict, Any, List
from pathlib import Path

from .client import AIRClient
from .config import AIRConfig
from .env_config import EnvConfig, load_env_config
from .logging import configure_logging, enable_verbose_logging, enable_debug_logging, sdk_logger
from .filter_builder import FilterBuilder, filter_builder, assets, tasks, cases, asset_tasks, acquisitions
from .constants import ALL_CONSTANTS

# Re-export everything from constants for easy access
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
    LogLevel, Defaults, Validation, ErrorMessages, FieldMappings
)

# Version information
__version__ = "2.0.0"
__air_version__ = "latest"  # Latest supported AIR version
__supported_air_versions__ = ["v1"]


class SDK:
    """
    Main SDK class providing easy access to all Binalyze AIR functionality.
    
    This class serves as the primary entry point and provides:
    - Easy configuration from .env files
    - Filter builder access
    - Constants access
    - Logging configuration
    - Client management
    """
    
    def __init__(self, 
                 host: Optional[str] = None,
                 api_token: Optional[str] = None,
                 organization_id: Optional[int] = None,
                 env_file: Optional[Union[str, Path]] = None,
                 config: Optional[Union[AIRConfig, EnvConfig]] = None,
                 enable_verbose: bool = False,
                 enable_debug: bool = False,
                 **kwargs):
        """
        Initialize the SDK.
        
        Args:
            host: AIR instance host URL
            api_token: API token for authentication
            organization_id: Default organization ID
            env_file: Path to .env file for configuration
            config: Pre-configured AIRConfig or EnvConfig instance
            enable_verbose: Enable verbose logging
            enable_debug: Enable debug logging with HTTP tracing
            **kwargs: Additional configuration options
        """
        self._client: Optional[AIRClient] = None
        self._config: Optional[AIRConfig] = None
        self._env_config: Optional[EnvConfig] = None
        
        # Configure logging first
        if enable_debug:
            enable_debug_logging()
        elif enable_verbose:
            enable_verbose_logging()
        
        # Load configuration
        if isinstance(config, EnvConfig):
            self._env_config = config
            # Convert EnvConfig to AIRConfig for client
            self._config = self._create_air_config_from_env(config)
        elif isinstance(config, AIRConfig):
            self._config = config
        else:
            # Try to load from environment/.env file
            if any([host, api_token, organization_id is not None]) or not env_file:
                # Use provided parameters
                self._config = AIRConfig.create(
                    host=host,
                    api_token=api_token,
                    organization_id=organization_id,
                    **kwargs
                )
            else:
                # Load from .env file
                self._env_config = load_env_config(env_file)
                self._config = self._create_air_config_from_env(self._env_config)
        
        # Validate configuration
        if not self._config:
            raise ValueError("No valid configuration provided")
        
        sdk_logger.info(f"Binalyze AIR SDK v{__version__} initialized")
        sdk_logger.debug(f"Configuration: {self._config}")
    
    def _create_air_config_from_env(self, env_config: EnvConfig) -> AIRConfig:
        """Create AIRConfig from EnvConfig."""
        config_data = {
            "host": env_config.air_host,
            "api_token": env_config.air_api_token,
            "organization_id": env_config.air_organization_id,
            "verify_ssl": env_config.air_verify_ssl,
            "timeout": env_config.air_timeout,
            "retry_count": env_config.air_retry_count,
            "retry_delay": env_config.air_retry_delay,
        }
        
        # Add fallback configuration if available
        if env_config.air_fallback_host:
            config_data["fallback_host"] = env_config.air_fallback_host
        if env_config.air_fallback_api_token:
            config_data["fallback_api_token"] = env_config.air_fallback_api_token
        
        return AIRConfig.create(**config_data)
    
    @property
    def client(self) -> AIRClient:
        """Get the AIR client instance."""
        if not self._client:
            self._client = AIRClient(config=self._config)
        return self._client
    
    @property
    def filter(self) -> FilterBuilder:
        """Get the filter builder."""
        return filter_builder
    
    @property
    def constants(self) -> Dict[str, Any]:
        """Get all SDK constants."""
        return ALL_CONSTANTS
    
    # Convenience properties for common operations
    @property
    def assets(self):
        """Access to assets API."""
        return self.client.assets
    
    @property
    def cases(self):
        """Access to cases API."""
        return self.client.cases
    
    @property
    def tasks(self):
        """Access to tasks API."""
        return self.client.tasks
    
    @property
    def acquisitions(self):
        """Access to acquisitions API."""
        return self.client.acquisitions
    
    @property
    def organizations(self):
        """Access to organizations API."""
        return self.client.organizations
    
    @property
    def audit(self):
        """Access to audit API."""
        return self.client.audit
    
    @property
    def triage(self):
        """Access to triage API."""
        return self.client.triage
    
    @property
    def policies(self):
        """Access to policies API."""
        return self.client.policies
    
    @property
    def baseline(self):
        """Access to baseline API."""
        return self.client.baseline
    
    @property
    def evidence(self):
        """Access to evidence API."""
        return self.client.evidence
    
    @property
    def user_management(self):
        """Access to user management API."""
        return self.client.user_management
    
    @property
    def auth(self):
        """Access to auth API."""
        return self.client.auth
    
    @property
    def auto_asset_tags(self):
        """Access to auto asset tags API."""
        return self.client.auto_asset_tags
    
    @property
    def event_subscription(self):
        """Access to event subscription API."""
        return self.client.event_subscription
    
    @property
    def interact(self):
        """Access to interact API."""
        return self.client.interact
    
    @property
    def params(self):
        """Access to params API."""
        return self.client.params
    
    @property
    def settings(self):
        """Access to settings API."""
        return self.client.settings
    
    @property
    def webhooks(self):
        """Access to webhooks API."""
        return self.client.webhooks
    
    @property
    def api_tokens(self):
        """Access to API tokens API."""
        return self.client.api_tokens
    
    @property
    def investigation_hub(self):
        """Access to investigation hub API."""
        return self.client.investigation_hub
    
    @property
    def cloud_forensics(self):
        """Access to cloud forensics API."""
        return self.client.cloud_forensics
    
    @property
    def backup(self):
        """Access to backup API."""
        return self.client.backup
    
    @property
    def license(self):
        """Access to license API."""
        return self.client.license
    
    @property
    def logger(self):
        """Access to logger API."""
        return self.client.logger
    
    @property
    def multipart_upload(self):
        """Access to multipart upload API."""
        return self.client.multipart_upload
    
    @property
    def notifications(self):
        """Access to notifications API."""
        return self.client.notifications
    
    @property
    def preset_filters(self):
        """Access to preset filters API."""
        return self.client.preset_filters
    
    @property
    def recent_activities(self):
        """Access to recent activities API."""
        return self.client.recent_activities
    
    @property
    def relay_server(self):
        """Access to relay server API."""
        return self.client.relay_server
    
    @property
    def webhook_executions(self):
        """Access to webhook executions API."""
        return self.client.webhook_executions
    
    def test_connection(self) -> bool:
        """Test the connection to AIR API."""
        return self.client.test_connection()
    
    def get_version_info(self) -> Dict[str, Union[str, List[str]]]:
        """Get version information."""
        return {
            "sdk_version": __version__,
            "supported_air_version": __air_version__,
            "supported_air_versions": __supported_air_versions__
        }
    
    def configure_logging(self, 
                         level: str = "INFO",
                         enable_console: bool = True,
                         enable_file: bool = False,
                         file_path: Optional[str] = None,
                         enable_http_trace: bool = False,
                         format_json: bool = False,
                         verbose: bool = False,
                         debug: bool = False):
        """Configure SDK logging."""
        configure_logging(
            level=level,
            enable_console=enable_console,
            enable_file=enable_file,
            file_path=file_path,
            enable_http_trace=enable_http_trace,
            format_json=format_json,
            verbose=verbose,
            debug=debug
        )
    
    def enable_verbose_logging(self):
        """Enable verbose logging."""
        enable_verbose_logging()
    
    def enable_debug_logging(self):
        """Enable debug logging with HTTP tracing."""
        enable_debug_logging()


# Factory functions for easy instantiation
def create_sdk(host: Optional[str] = None,
               api_token: Optional[str] = None,
               organization_id: Optional[int] = None,
               env_file: Optional[Union[str, Path]] = None,
               **kwargs) -> SDK:
    """
    Create SDK instance with provided parameters.
    
    Args:
        host: AIR instance host URL
        api_token: API token for authentication
        organization_id: Default organization ID
        env_file: Path to .env file for configuration
        **kwargs: Additional configuration options
        
    Returns:
        SDK instance
    """
    return SDK(
        host=host,
        api_token=api_token,
        organization_id=organization_id,
        env_file=env_file,
        **kwargs
    )


def create_sdk_from_env(env_file: Optional[Union[str, Path]] = None, **kwargs) -> SDK:
    """
    Create SDK instance from environment/.env configuration.
    
    Args:
        env_file: Path to .env file
        **kwargs: Additional configuration options
        
    Returns:
        SDK instance configured from environment
    """
    env_config = load_env_config(env_file)
    return SDK(config=env_config, **kwargs)


def create_sdk_with_debug(host: Optional[str] = None,
                         api_token: Optional[str] = None,
                         organization_id: Optional[int] = None,
                         **kwargs) -> SDK:
    """
    Create SDK instance with debug logging enabled.
    
    Args:
        host: AIR instance host URL
        api_token: API token for authentication
        organization_id: Default organization ID
        **kwargs: Additional configuration options
        
    Returns:
        SDK instance with debug logging enabled
    """
    return SDK(
        host=host,
        api_token=api_token,
        organization_id=organization_id,
        enable_debug=True,
        **kwargs
    )


def create_sdk_with_verbose(host: Optional[str] = None,
                           api_token: Optional[str] = None,
                           organization_id: Optional[int] = None,
                           **kwargs) -> SDK:
    """
    Create SDK instance with verbose logging enabled.
    
    Args:
        host: AIR instance host URL
        api_token: API token for authentication
        organization_id: Default organization ID
        **kwargs: Additional configuration options
        
    Returns:
        SDK instance with verbose logging enabled
    """
    return SDK(
        host=host,
        api_token=api_token,
        organization_id=organization_id,
        enable_verbose=True,
        **kwargs
    )


# Default SDK instance - can be configured and used directly
sdk = None

def get_sdk() -> Optional[SDK]:
    """Get the default SDK instance."""
    return sdk

def set_default_sdk(sdk_instance: SDK):
    """Set the default SDK instance."""
    global sdk
    sdk = sdk_instance

# Example usage patterns:
"""
# Basic usage with parameters
sdk = create_sdk(
    host="https://your-air-instance.com",
    api_token="your-token",
    organization_id=0
)

# Usage with .env file
sdk = create_sdk_from_env(".env")

# Usage with debug logging
sdk = create_sdk_with_debug(
    host="https://your-air-instance.com",
    api_token="your-token",
    organization_id=0
)

# Using filter builder (as requested in the user query)
builder = sdk.filter
my_filter = builder.asset().add_included_endpoints(['endpoint1']).add_organization(0).build()

# Alternative syntax
my_filter = assets().is_online().is_windows().add_organization(0).build()

# Using constants
print(sdk.constants["ASSET_STATUS"].ONLINE)
print(AssetStatus.ONLINE)

# API usage
assets_list = sdk.assets.get_assets(filter=my_filter)
cases_list = sdk.cases.get_cases()
""" 