"""Configuration management for credit-risk-creditum package."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from .exceptions import ConfigurationError


class Config:
    """Configuration management class."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (JSON format)
        """
        self._config: Dict[str, Any] = self._load_defaults()
        
        # Load from environment variables
        self._load_from_env()
        
        # Load from file if provided
        if config_file:
            self._load_from_file(config_file)
    
    def _load_defaults(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            'credit_application': {
                'min_credit_score': 600,
                'max_dti': 0.43,
                'default_loan_term_months': 60
            },
            'economic_indicators': {
                'update_frequency_hours': 24,
                'default_gdp_growth': 0.025,
                'default_unemployment_rate': 0.045,
                'default_inflation_rate': 0.02,
                'default_interest_rate': 0.035
            },
            'risk_assessment': {
                'individual_weights': {
                    'payment_history': 0.30,
                    'credit_utilization': 0.25,
                    'credit_history_length': 0.15,
                    'income_stability': 0.15,
                    'debt_to_income': 0.15
                },
                'corporate_weights': {
                    'financial_ratios': 0.25,
                    'market_position': 0.20,
                    'operational_efficiency': 0.15,
                    'management_quality': 0.15,
                    'business_model': 0.15,
                    'regulatory_compliance': 0.10
                },
                'risk_thresholds': {
                    'low': 0.3,
                    'medium': 0.6,
                    'high': 0.8
                }
            },
            'stress_testing': {
                'enabled_scenarios': ['recession', 'inflation_surge', 'market_crash', 'optimistic'],
                'default_scenarios': ['recession', 'market_crash']
            },
            'logging': {
                'level': 'INFO',
                'format': 'standard',
                'file': None
            },
            'performance': {
                'cache_enabled': True,
                'cache_ttl_seconds': 3600,
                'max_concurrent_assessments': 100
            }
        }
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'CREDIT_RISK_MIN_CREDIT_SCORE': ('credit_application', 'min_credit_score', int),
            'CREDIT_RISK_MAX_DTI': ('credit_application', 'max_dti', float),
            'CREDIT_RISK_LOG_LEVEL': ('logging', 'level', str),
            'CREDIT_RISK_LOG_FILE': ('logging', 'file', str),
            'CREDIT_RISK_CACHE_ENABLED': ('performance', 'cache_enabled', lambda x: x.lower() == 'true'),
            'CREDIT_RISK_CACHE_TTL': ('performance', 'cache_ttl_seconds', int),
        }
        
        for env_var, (section, key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = converter(value)
                    if section not in self._config:
                        self._config[section] = {}
                    self._config[section][key] = converted_value
                except (ValueError, TypeError) as e:
                    raise ConfigurationError(f"Invalid value for {env_var}: {value}") from e
    
    def _load_from_file(self, config_file: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            # Merge file configuration with existing configuration
            self._merge_config(file_config)
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}") from e
        except IOError as e:
            raise ConfigurationError(f"Error reading configuration file: {e}") from e
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge new configuration with existing configuration.
        
        Args:
            new_config: New configuration dictionary
        """
        def merge_dict(base_dict: dict, new_dict: dict) -> dict:
            for key, value in new_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    merge_dict(base_dict[key], value)
                else:
                    base_dict[key] = value
            return base_dict
        
        merge_dict(self._config, new_config)
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key (optional)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        if section not in self._config:
            return default
        
        section_config = self._config[section]
        
        if key is None:
            return section_config
        
        return section_config.get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
    
    def save_to_file(self, config_file: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config_file: Path to save configuration file
        """
        config_path = Path(config_file)
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
                
        except IOError as e:
            raise ConfigurationError(f"Error writing configuration file: {e}") from e
    
    def validate(self) -> None:
        """Validate configuration values."""
        # Validate credit application settings
        credit_config = self.get('credit_application', default={})
        min_score = credit_config.get('min_credit_score', 600)
        max_dti = credit_config.get('max_dti', 0.43)
        
        if not 300 <= min_score <= 850:
            raise ConfigurationError(f"min_credit_score must be between 300 and 850, got {min_score}")
        
        if not 0 < max_dti <= 1.0:
            raise ConfigurationError(f"max_dti must be between 0 and 1.0, got {max_dti}")
        
        # Validate risk thresholds
        risk_config = self.get('risk_assessment', 'risk_thresholds', {})
        thresholds = [risk_config.get('low', 0.3), risk_config.get('medium', 0.6), risk_config.get('high', 0.8)]
        
        if not all(0 <= t <= 1.0 for t in thresholds):
            raise ConfigurationError("Risk thresholds must be between 0 and 1.0")
        
        if not (thresholds[0] < thresholds[1] < thresholds[2]):
            raise ConfigurationError("Risk thresholds must be in ascending order: low < medium < high")


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.
    
    Returns:
        Global configuration instance
    """
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config) -> None:
    """
    Set global configuration instance.
    
    Args:
        config: Configuration instance
    """
    global _global_config
    _global_config = config


def load_config_from_file(config_file: str) -> Config:
    """
    Load configuration from file and set as global.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration instance
    """
    config = Config(config_file)
    set_config(config)
    return config