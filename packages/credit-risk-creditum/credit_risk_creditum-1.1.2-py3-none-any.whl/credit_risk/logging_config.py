"""Logging configuration for credit-risk-creditum package."""

import logging
import logging.config
import os
from typing import Dict, Any


def get_logging_config(log_level: str = "INFO", log_file: str = None) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Logging configuration dictionary
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'credit_risk': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        config['handlers']['file'] = {
            'level': log_level,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        config['loggers']['credit_risk']['handlers'].append('file')
        config['root']['handlers'].append('file')
    
    return config


def setup_logging(log_level: str = None, log_file: str = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (defaults to INFO or CREDIT_RISK_LOG_LEVEL env var)
        log_file: Log file path (defaults to CREDIT_RISK_LOG_FILE env var)
    """
    # Get configuration from environment variables if not provided
    if log_level is None:
        log_level = os.getenv('CREDIT_RISK_LOG_LEVEL', 'INFO')
    
    if log_file is None:
        log_file = os.getenv('CREDIT_RISK_LOG_FILE')
    
    # Get and apply logging configuration
    config = get_logging_config(log_level, log_file)
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f'credit_risk.{name}')


# Default logger for the package
logger = get_logger('main')