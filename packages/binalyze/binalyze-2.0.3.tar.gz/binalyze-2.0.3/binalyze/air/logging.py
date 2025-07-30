"""
Logging system for the Binalyze AIR SDK.

Provides comprehensive logging with different levels including HTTP trace logging.
"""

import logging
import sys
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from .constants import LogLevel


class SDKFormatter(logging.Formatter):
    """Custom formatter for SDK logging."""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with SDK-specific formatting."""
        parts = []
        
        if self.include_timestamp:
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            parts.append(f"[{timestamp}]")
        
        if self.include_level:
            parts.append(f"[{record.levelname}]")
        
        parts.append(f"[{record.name}]")
        parts.append(record.getMessage())
        
        return " ".join(parts)


class HTTPTraceLogger:
    """Logger specifically for HTTP request/response tracing."""
    
    def __init__(self, logger_name: str = "binalyze.air.http"):
        self.logger = logging.getLogger(logger_name)
        self.start_times: Dict[str, float] = {}
    
    def log_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, 
                   body: Optional[Any] = None, request_id: Optional[str] = None) -> str:
        """Log HTTP request details."""
        if not request_id:
            request_id = f"req_{int(time.time() * 1000)}"
        
        self.start_times[request_id] = time.time()
        
        log_data: Dict[str, Any] = {
            "request_id": request_id,
            "method": method,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        
        if headers:
            # Filter sensitive headers
            safe_headers = {k: v for k, v in headers.items() 
                          if k.lower() not in ['authorization', 'x-api-key', 'x-auth-token']}
            if safe_headers:
                log_data["headers"] = dict(safe_headers)
        
        if body and self.logger.isEnabledFor(logging.DEBUG):
            try:
                if isinstance(body, (dict, list)):
                    log_data["body"] = body
                elif isinstance(body, str):
                    # Try to parse as JSON for better formatting
                    try:
                        log_data["body"] = json.loads(body)
                    except json.JSONDecodeError:
                        log_data["body"] = body[:1000] + "..." if len(body) > 1000 else body
                else:
                    log_data["body"] = str(body)[:1000] + "..." if len(str(body)) > 1000 else str(body)
            except Exception:
                log_data["body"] = "<unable to serialize>"
        
        self.logger.info(f"HTTP Request: {json.dumps(log_data, indent=2)}")
        return request_id
    
    def log_response(self, request_id: str, status_code: int, headers: Optional[Dict[str, str]] = None,
                    body: Optional[Any] = None, error: Optional[Exception] = None):
        """Log HTTP response details."""
        duration = None
        if request_id in self.start_times:
            duration = time.time() - self.start_times[request_id]
            del self.start_times[request_id]
        
        log_data = {
            "request_id": request_id,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        
        if duration is not None:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        if headers:
            safe_headers = {k: v for k, v in headers.items() 
                          if k.lower() not in ['set-cookie', 'authorization']}
            if safe_headers:
                log_data["headers"] = safe_headers
        
        if error:
            log_data["error"] = {
                "type": type(error).__name__,
                "message": str(error)
            }
            self.logger.error(f"HTTP Response (Error): {json.dumps(log_data, indent=2)}")
        else:
            if body and self.logger.isEnabledFor(logging.DEBUG):
                try:
                    if isinstance(body, (dict, list)):
                        log_data["body"] = body
                    elif isinstance(body, str):
                        try:
                            log_data["body"] = json.loads(body)
                        except json.JSONDecodeError:
                            log_data["body"] = body[:1000] + "..." if len(body) > 1000 else body
                    else:
                        log_data["body"] = str(body)[:1000] + "..." if len(str(body)) > 1000 else str(body)
                except Exception:
                    log_data["body"] = "<unable to serialize>"
            
            level = logging.INFO if status_code < 400 else logging.WARNING
            self.logger.log(level, f"HTTP Response: {json.dumps(log_data, indent=2)}")


class SDKLogger:
    """Main SDK logger with configuration options."""
    
    def __init__(self, name: str = "binalyze.air"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.http_logger = HTTPTraceLogger()
        self._configured = False
    
    def configure(self, 
                 level: str = LogLevel.INFO,
                 enable_console: bool = True,
                 enable_file: bool = False,
                 file_path: Optional[str] = None,
                 enable_http_trace: bool = False,
                 format_json: bool = False,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """Configure the SDK logger."""
        # Allow reconfiguration for inheritance from global config
        # if self._configured:
        #     return
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set level
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        
        # Configure console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            
            if format_json:
                console_formatter = JSONFormatter()
            else:
                console_formatter = SDKFormatter()
            
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # Configure file handler
        if enable_file and file_path:
            from logging.handlers import RotatingFileHandler
            
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setLevel(numeric_level)
            
            if format_json:
                file_formatter = JSONFormatter()
            else:
                file_formatter = SDKFormatter()
            
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Configure HTTP trace logging
        if enable_http_trace:
            self.http_logger.logger.setLevel(logging.DEBUG)
            # Add handlers to HTTP logger if not already present
            if not self.http_logger.logger.handlers:
                for handler in self.logger.handlers:
                    self.http_logger.logger.addHandler(handler)
        
        self._configured = True
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.logger.debug(message, extra=extra or {})
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.logger.info(message, extra=extra or {})
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.logger.error(message, extra=extra or {})
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.logger.critical(message, extra=extra or {})
    
    def log_api_call(self, api_name: str, method: str, endpoint: str, 
                    params: Optional[Dict[str, Any]] = None, 
                    success: bool = True, 
                    duration: Optional[float] = None,
                    response_size: Optional[int] = None):
        """Log API call information."""
        log_data = {
            "api_name": api_name,
            "method": method,
            "endpoint": endpoint,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if params:
            log_data["params"] = params
        
        if duration is not None:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        if response_size is not None:
            log_data["response_size_bytes"] = response_size
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, f"API Call: {json.dumps(log_data)}")
    
    def log_filter_usage(self, filter_type: str, filter_data: Dict[str, Any]):
        """Log filter usage for debugging."""
        log_data = {
            "filter_type": filter_type,
            "filter_data": filter_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.debug(f"Filter Usage: {json.dumps(log_data)}")
    
    def get_http_tracer(self) -> HTTPTraceLogger:
        """Get HTTP trace logger."""
        return self.http_logger


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            extra_fields = {k: v for k, v in record.__dict__.items() 
                          if k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                                     'filename', 'module', 'lineno', 'funcName', 'created', 
                                     'msecs', 'relativeCreated', 'thread', 'threadName', 
                                     'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 
                                     'stack_info', 'message']}
            if extra_fields:
                log_data.update(extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# Global logger instance and configuration
sdk_logger = SDKLogger()
_global_config = {}

# Convenience functions
def get_logger(name: Optional[str] = None) -> SDKLogger:
    """Get SDK logger instance that inherits global configuration."""
    if name:
        logger = SDKLogger(name)
        # Apply global configuration if it exists
        if _global_config:
            logger.configure(**_global_config)
        return logger
    return sdk_logger

def configure_logging(level: str = LogLevel.INFO,
                     enable_console: bool = True,
                     enable_file: bool = False,
                     file_path: Optional[str] = None,
                     enable_http_trace: bool = False,
                     format_json: bool = False,
                     verbose: bool = False,
                     debug: bool = False):
    """Configure SDK logging with convenience options."""
    global _global_config
    
    if debug:
        level = LogLevel.DEBUG
        enable_http_trace = True
    elif verbose:
        level = LogLevel.INFO
        enable_http_trace = True
    
    # Store global configuration for new loggers
    _global_config = {
        'level': level,
        'enable_console': enable_console,
        'enable_file': enable_file,
        'file_path': file_path,
        'enable_http_trace': enable_http_trace,
        'format_json': format_json
    }
    
    # Configure the main SDK logger
    sdk_logger.configure(**_global_config)

def enable_verbose_logging():
    """Enable verbose logging (INFO level with HTTP trace)."""
    configure_logging(
        level=LogLevel.INFO,
        enable_http_trace=True,
        verbose=True
    )

def enable_debug_logging():
    """Enable debug logging (DEBUG level with full HTTP trace)."""
    configure_logging(
        level=LogLevel.DEBUG,
        enable_http_trace=True,
        debug=True
    )

def disable_logging():
    """Disable all SDK logging."""
    sdk_logger.logger.setLevel(logging.CRITICAL + 1)
    sdk_logger.http_logger.logger.setLevel(logging.CRITICAL + 1)


# Performance logging utilities
class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger: Optional[SDKLogger] = None):
        self.operation_name = operation_name
        self.logger = logger or sdk_logger
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        if self.start_time is not None:
            duration = self.end_time - self.start_time
            
            if exc_type is None:
                self.logger.info(f"Completed operation: {self.operation_name} in {duration:.3f}s")
            else:
                self.logger.error(f"Failed operation: {self.operation_name} after {duration:.3f}s - {exc_val}")
        else:
            self.logger.error(f"Failed operation: {self.operation_name} - start time not recorded")


def performance_timer(operation_name: str, logger: Optional[SDKLogger] = None):
    """Create a performance timer context manager."""
    return PerformanceTimer(operation_name, logger)


# Example usage:
"""
# Basic configuration
configure_logging(level=LogLevel.INFO, enable_console=True)

# Enable verbose logging
enable_verbose_logging()

# Enable debug logging with HTTP tracing
enable_debug_logging()

# Custom configuration
configure_logging(
    level=LogLevel.DEBUG,
    enable_console=True,
    enable_file=True,
    file_path="/tmp/binalyze_air_sdk.log",
    enable_http_trace=True,
    format_json=True
)

# Usage in code
logger = get_logger("my_module")
logger.info("Starting operation")

# Performance timing
with performance_timer("asset_retrieval"):
    assets = client.assets.get_assets()
""" 