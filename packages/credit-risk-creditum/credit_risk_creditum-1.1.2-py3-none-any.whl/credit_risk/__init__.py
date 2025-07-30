"""
Credit Risk Assessment Package

A comprehensive credit risk assessment framework that evaluates both individual 
and corporate credit applications, incorporating economic indicators and 
stress testing capabilities.
"""

# Core components
from .core.application import CreditApplication
from .core.economic import EconomicIndicators

# Risk assessment models
from .models.individual import IndividualRiskAssessment
from .models.corporate import CorporateRiskAssessment
from .models.base import BaseRiskAssessment

# Configuration and utilities
from .config import Config, get_config, set_config, load_config_from_file
from .logging_config import setup_logging, get_logger

# Exception classes
from .exceptions import (
    CreditRiskError,
    ValidationError,
    EconomicDataError,
    ModelError,
    StressTestError,
    ConfigurationError,
    DataProcessingError,
    InsufficientDataError,
    RiskCalculationError,
)

__version__ = "1.1.2"
__author__ = "Omoshola Owolabi"
__email__ = "owolabi.omoshola@outlook.com"
__description__ = "Advanced credit risk assessment and stress testing with real-time economic data integration"
__url__ = "https://github.com/credit-risk-creditum/creditum"
__license__ = "MIT"

# Main public API
__all__ = [
    # Core classes
    "CreditApplication",
    "EconomicIndicators",
    
    # Risk assessment models
    "IndividualRiskAssessment",
    "CorporateRiskAssessment", 
    "BaseRiskAssessment",
    
    # Configuration
    "Config",
    "get_config",
    "set_config",
    "load_config_from_file",
    
    # Logging
    "setup_logging",
    "get_logger",
    
    # Exceptions
    "CreditRiskError",
    "ValidationError",
    "EconomicDataError",
    "ModelError",
    "StressTestError",
    "ConfigurationError",
    "DataProcessingError",
    "InsufficientDataError",
    "RiskCalculationError",
]

# Package metadata
__package_info__ = {
    "name": "credit-risk-creditum",
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "description": __description__,
    "url": __url__,
    "license": __license__,
}