"""
Structured logging configuration for GoWheels
Provides JSON logging with correlation IDs and context
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """JSON formatter with correlation IDs and structured fields"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', None),
            'user_id': getattr(record, 'user_id', None),
            'ip_address': getattr(record, 'ip_address', None),
            'request_method': getattr(record, 'request_method', None),
            'request_path': getattr(record, 'request_path', None),
            'response_status': getattr(record, 'response_status', None),
            'duration_ms': getattr(record, 'duration_ms', None),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        return json.dumps(log_data)


def get_correlation_id() -> str:
    """Generate a unique correlation ID for request tracking"""
    return str(uuid.uuid4())


class CorrelationLogger:
    """Logger with automatic correlation ID injection"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.correlation_id = None
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for this logger instance"""
        self.correlation_id = correlation_id
    
    def _log(self, level: int, msg: str, **kwargs):
        """Internal log method with correlation ID"""
        extra = kwargs.pop('extra', {})
        if self.correlation_id:
            extra['correlation_id'] = self.correlation_id
        self.logger.log(level, msg, extra=extra, **kwargs)
    
    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)


# Django logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'structured': {
            '()': 'gowheels.logging_config.StructuredFormatter',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/gowheels.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'structured',
            'level': 'INFO',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/errors.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'structured',
            'level': 'ERROR',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'formatter': 'structured',
            'level': 'INFO',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'gowheels': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'gowheels.security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gowheels.performance': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
