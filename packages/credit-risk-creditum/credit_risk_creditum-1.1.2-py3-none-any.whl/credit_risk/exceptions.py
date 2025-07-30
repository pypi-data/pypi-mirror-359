"""Custom exceptions for credit-risk-creditum package."""


class CreditRiskError(Exception):
    """Base exception for credit risk assessment errors."""
    pass


class ValidationError(CreditRiskError):
    """Raised when application data validation fails."""
    pass


class EconomicDataError(CreditRiskError):
    """Raised when economic data is invalid or missing."""
    pass


class ModelError(CreditRiskError):
    """Raised when there's an error with risk assessment models."""
    pass


class StressTestError(CreditRiskError):
    """Raised when stress testing encounters an error."""
    pass


class ConfigurationError(CreditRiskError):
    """Raised when there's a configuration issue."""
    pass


class DataProcessingError(CreditRiskError):
    """Raised when data processing fails."""
    pass


class InsufficientDataError(CreditRiskError):
    """Raised when there's insufficient data for assessment."""
    pass


class RiskCalculationError(CreditRiskError):
    """Raised when risk calculation fails."""
    pass