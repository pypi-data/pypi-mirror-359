"""
Environment configuration support for the Binalyze AIR SDK.

Supports loading configuration from .env files for easy Jupyter Notebook sharing.
"""

import os
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


@dataclass
class EnvConfig:
    """Environment-based configuration for the SDK."""
    
    # AIR Connection Settings
    air_host: Optional[str] = None
    air_api_token: Optional[str] = None
    air_organization_id: Optional[int] = None
    
    # Additional Connection Settings
    air_verify_ssl: bool = True
    air_timeout: int = 30
    air_retry_count: int = 3
    air_retry_delay: float = 1.0
    
    # Fallback/Secondary Server Settings
    air_fallback_host: Optional[str] = None
    air_fallback_api_token: Optional[str] = None
    
    # Logging Configuration
    air_log_level: str = "INFO"
    air_log_file: Optional[str] = None
    air_enable_http_trace: bool = False
    air_enable_verbose: bool = False
    air_enable_debug: bool = False
    
    # Performance Settings
    air_max_page_size: int = 1000
    air_default_page_size: int = 100
    air_connection_pool_size: int = 10
    
    # Feature Flags
    air_enable_caching: bool = False
    air_cache_ttl: int = 300  # 5 minutes
    air_enable_rate_limiting: bool = True
    
    # Development Settings
    air_dev_mode: bool = False
    air_mock_responses: bool = False
    
    # Version and Compatibility
    air_version: str = "latest"
    air_supported_versions: str = "v1"
    
    # Security Settings
    air_mask_sensitive_data: bool = True
    air_log_request_body: bool = False
    air_log_response_body: bool = False
    
    @classmethod
    def from_env(cls, env_file: Optional[Union[str, Path]] = None, 
                 load_dotenv_file: bool = True) -> 'EnvConfig':
        """
        Create configuration from environment variables.
        
        Args:
            env_file: Path to .env file to load
            load_dotenv_file: Whether to load .env file if available
            
        Returns:
            EnvConfig instance with values from environment
        """
        # Load .env file if available and requested
        if load_dotenv_file and DOTENV_AVAILABLE:
            if env_file:
                env_path = Path(env_file)
                if env_path.exists():
                    load_dotenv(env_path)
            else:
                # Try common .env file locations
                for env_path in [Path(".env"), Path("../.env"), Path("../../.env")]:
                    if env_path.exists():
                        load_dotenv(env_path)
                        break
        
        # Extract values from environment
        config = cls()
        
        # AIR Connection Settings
        config.air_host = os.getenv("AIR_HOST") or os.getenv("BINALYZE_AIR_HOST")
        config.air_api_token = os.getenv("AIR_API_TOKEN") or os.getenv("BINALYZE_AIR_API_TOKEN")
        
        org_id_str = os.getenv("AIR_ORGANIZATION_ID") or os.getenv("BINALYZE_AIR_ORGANIZATION_ID")
        if org_id_str:
            try:
                config.air_organization_id = int(org_id_str)
            except ValueError:
                pass
        
        # Additional Connection Settings
        ssl_verify = os.getenv("AIR_VERIFY_SSL", "true").lower()
        config.air_verify_ssl = ssl_verify in ("true", "1", "yes", "on")
        
        timeout_str = os.getenv("AIR_TIMEOUT", "30")
        try:
            config.air_timeout = int(timeout_str)
        except ValueError:
            pass
        
        retry_count_str = os.getenv("AIR_RETRY_COUNT", "3")
        try:
            config.air_retry_count = int(retry_count_str)
        except ValueError:
            pass
        
        retry_delay_str = os.getenv("AIR_RETRY_DELAY", "1.0")
        try:
            config.air_retry_delay = float(retry_delay_str)
        except ValueError:
            pass
        
        # Fallback Server Settings
        config.air_fallback_host = os.getenv("AIR_FALLBACK_HOST") or os.getenv("BINALYZE_AIR_FALLBACK_HOST")
        config.air_fallback_api_token = os.getenv("AIR_FALLBACK_API_TOKEN") or os.getenv("BINALYZE_AIR_FALLBACK_API_TOKEN")
        
        # Logging Configuration
        config.air_log_level = os.getenv("AIR_LOG_LEVEL", "INFO").upper()
        config.air_log_file = os.getenv("AIR_LOG_FILE")
        
        http_trace = os.getenv("AIR_ENABLE_HTTP_TRACE", "false").lower()
        config.air_enable_http_trace = http_trace in ("true", "1", "yes", "on")
        
        verbose = os.getenv("AIR_ENABLE_VERBOSE", "false").lower()
        config.air_enable_verbose = verbose in ("true", "1", "yes", "on")
        
        debug = os.getenv("AIR_ENABLE_DEBUG", "false").lower()
        config.air_enable_debug = debug in ("true", "1", "yes", "on")
        
        # Performance Settings
        max_page_str = os.getenv("AIR_MAX_PAGE_SIZE", "1000")
        try:
            config.air_max_page_size = int(max_page_str)
        except ValueError:
            pass
        
        default_page_str = os.getenv("AIR_DEFAULT_PAGE_SIZE", "100")
        try:
            config.air_default_page_size = int(default_page_str)
        except ValueError:
            pass
        
        pool_size_str = os.getenv("AIR_CONNECTION_POOL_SIZE", "10")
        try:
            config.air_connection_pool_size = int(pool_size_str)
        except ValueError:
            pass
        
        # Feature Flags
        caching = os.getenv("AIR_ENABLE_CACHING", "false").lower()
        config.air_enable_caching = caching in ("true", "1", "yes", "on")
        
        cache_ttl_str = os.getenv("AIR_CACHE_TTL", "300")
        try:
            config.air_cache_ttl = int(cache_ttl_str)
        except ValueError:
            pass
        
        rate_limiting = os.getenv("AIR_ENABLE_RATE_LIMITING", "true").lower()
        config.air_enable_rate_limiting = rate_limiting in ("true", "1", "yes", "on")
        
        # Development Settings
        dev_mode = os.getenv("AIR_DEV_MODE", "false").lower()
        config.air_dev_mode = dev_mode in ("true", "1", "yes", "on")
        
        mock_responses = os.getenv("AIR_MOCK_RESPONSES", "false").lower()
        config.air_mock_responses = mock_responses in ("true", "1", "yes", "on")
        
        # Version Settings
        config.air_version = os.getenv("AIR_VERSION", "latest")
        config.air_supported_versions = os.getenv("AIR_SUPPORTED_VERSIONS", "v1")
        
        # Security Settings
        mask_sensitive = os.getenv("AIR_MASK_SENSITIVE_DATA", "true").lower()
        config.air_mask_sensitive_data = mask_sensitive in ("true", "1", "yes", "on")
        
        log_req_body = os.getenv("AIR_LOG_REQUEST_BODY", "false").lower()
        config.air_log_request_body = log_req_body in ("true", "1", "yes", "on")
        
        log_resp_body = os.getenv("AIR_LOG_RESPONSE_BODY", "false").lower()
        config.air_log_response_body = log_resp_body in ("true", "1", "yes", "on")
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            dataclass_field.name: getattr(self, dataclass_field.name)
            for dataclass_field in self.__class__.__dataclass_fields__.values()
        }
    
    def to_env_dict(self) -> Dict[str, str]:
        """Convert configuration to environment variable dictionary."""
        env_dict = {}
        
        for field_name, field_obj in self.__class__.__dataclass_fields__.items():
            value = getattr(self, field_name)
            if value is not None:
                env_name = field_name.upper()
                if isinstance(value, bool):
                    env_dict[env_name] = "true" if value else "false"
                else:
                    env_dict[env_name] = str(value)
        
        return env_dict
    
    def save_to_env_file(self, file_path: Union[str, Path]):
        """Save configuration to .env file."""
        env_dict = self.to_env_dict()
        
        with open(file_path, 'w') as f:
            f.write("# Binalyze AIR SDK Configuration\n")
            f.write("# Generated automatically - modify as needed\n\n")
            
            # Connection settings
            f.write("# AIR Connection Settings\n")
            for key in ["AIR_HOST", "AIR_API_TOKEN", "AIR_ORGANIZATION_ID"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Additional connection settings
            f.write("# Connection Options\n")
            for key in ["AIR_VERIFY_SSL", "AIR_TIMEOUT", "AIR_RETRY_COUNT", "AIR_RETRY_DELAY"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Fallback settings
            f.write("# Fallback Server Settings\n")
            for key in ["AIR_FALLBACK_HOST", "AIR_FALLBACK_API_TOKEN"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Logging settings
            f.write("# Logging Configuration\n")
            for key in ["AIR_LOG_LEVEL", "AIR_LOG_FILE", "AIR_ENABLE_HTTP_TRACE", 
                       "AIR_ENABLE_VERBOSE", "AIR_ENABLE_DEBUG"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Performance settings
            f.write("# Performance Settings\n")
            for key in ["AIR_MAX_PAGE_SIZE", "AIR_DEFAULT_PAGE_SIZE", "AIR_CONNECTION_POOL_SIZE"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Feature flags
            f.write("# Feature Flags\n")
            for key in ["AIR_ENABLE_CACHING", "AIR_CACHE_TTL", "AIR_ENABLE_RATE_LIMITING"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Development settings
            f.write("# Development Settings\n")
            for key in ["AIR_DEV_MODE", "AIR_MOCK_RESPONSES"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Version settings
            f.write("# Version and Compatibility\n")
            for key in ["AIR_VERSION", "AIR_SUPPORTED_VERSIONS"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
            f.write("\n")
            
            # Security settings
            f.write("# Security Settings\n")
            for key in ["AIR_MASK_SENSITIVE_DATA", "AIR_LOG_REQUEST_BODY", "AIR_LOG_RESPONSE_BODY"]:
                if key in env_dict:
                    f.write(f"{key}={env_dict[key]}\n")
    
    def validate(self) -> bool:
        """Validate the configuration."""
        if not self.air_host:
            return False
        
        if not self.air_api_token:
            return False
        
        if self.air_organization_id is None:
            return False
        
        return True
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors."""
        errors = []
        
        if not self.air_host:
            errors.append("AIR_HOST is required")
        
        if not self.air_api_token:
            errors.append("AIR_API_TOKEN is required")
        
        if self.air_organization_id is None:
            errors.append("AIR_ORGANIZATION_ID is required")
        
        return errors


def load_env_config(env_file: Optional[Union[str, Path]] = None) -> EnvConfig:
    """
    Load environment configuration from .env file and environment variables.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        EnvConfig instance
    """
    return EnvConfig.from_env(env_file)


def create_sample_env_file(file_path: Union[str, Path] = ".env.sample"):
    """
    Create a sample .env file with all available configuration options.
    
    Args:
        file_path: Path where to create the sample file
    """
    sample_config = EnvConfig(
        air_host="https://your-air-instance.com",
        air_api_token="your-api-token-here",
        air_organization_id=0,
        air_verify_ssl=True,
        air_timeout=30,
        air_retry_count=3,
        air_retry_delay=1.0,
        air_fallback_host="https://your-fallback-air-instance.com",
        air_fallback_api_token="your-fallback-api-token-here",
        air_log_level="INFO",
        air_log_file="/tmp/binalyze_air_sdk.log",
        air_enable_http_trace=False,
        air_enable_verbose=False,
        air_enable_debug=False,
        air_max_page_size=1000,
        air_default_page_size=100,
        air_connection_pool_size=10,
        air_enable_caching=False,
        air_cache_ttl=300,
        air_enable_rate_limiting=True,
        air_dev_mode=False,
        air_mock_responses=False,
        air_version="latest",
        air_supported_versions="v1",
        air_mask_sensitive_data=True,
        air_log_request_body=False,
        air_log_response_body=False
    )
    
    sample_config.save_to_env_file(file_path)


# Example usage and sample .env content
SAMPLE_ENV_CONTENT = """
# Binalyze AIR SDK Configuration
# Copy this to .env and update with your values

# AIR Connection Settings (Required)
AIR_HOST=https://your-air-instance.com
AIR_API_TOKEN=your-api-token-here
AIR_ORGANIZATION_ID=0

# Connection Options
AIR_VERIFY_SSL=true
AIR_TIMEOUT=30
AIR_RETRY_COUNT=3
AIR_RETRY_DELAY=1.0

# Fallback Server Settings (Optional)
# AIR_FALLBACK_HOST=https://your-fallback-air-instance.com
# AIR_FALLBACK_API_TOKEN=your-fallback-api-token-here

# Logging Configuration
AIR_LOG_LEVEL=INFO
# AIR_LOG_FILE=/tmp/binalyze_air_sdk.log
AIR_ENABLE_HTTP_TRACE=false
AIR_ENABLE_VERBOSE=false
AIR_ENABLE_DEBUG=false

# Performance Settings
AIR_MAX_PAGE_SIZE=1000
AIR_DEFAULT_PAGE_SIZE=100
AIR_CONNECTION_POOL_SIZE=10

# Feature Flags
AIR_ENABLE_CACHING=false
AIR_CACHE_TTL=300
AIR_ENABLE_RATE_LIMITING=true

# Development Settings
AIR_DEV_MODE=false
AIR_MOCK_RESPONSES=false

# Version and Compatibility
AIR_VERSION=latest
AIR_SUPPORTED_VERSIONS=v1

# Security Settings
AIR_MASK_SENSITIVE_DATA=true
AIR_LOG_REQUEST_BODY=false
AIR_LOG_RESPONSE_BODY=false
""" 