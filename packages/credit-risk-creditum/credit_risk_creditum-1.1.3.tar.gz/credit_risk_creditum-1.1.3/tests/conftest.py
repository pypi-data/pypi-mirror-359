"""Pytest configuration and fixtures."""

import pytest
from credit_risk.core.application import CreditApplication
from credit_risk.core.economic import EconomicIndicators


@pytest.fixture
def sample_individual_application():
    """Sample individual credit application data."""
    return {
        'credit_score': 720,
        'monthly_income': 5000,
        'monthly_debt': 1500,
        'loan_amount': 25000,
        'loan_purpose': 'home_improvement'
    }


@pytest.fixture
def sample_corporate_application():
    """Sample corporate credit application data."""
    return {
        'years_in_business': 5,
        'annual_revenue': 500000,
        'industry': 'technology',
        'loan_amount': 100000,
        'loan_purpose': 'expansion'
    }


@pytest.fixture
def sample_economic_data():
    """Sample economic indicators data."""
    return {
        'cpi': 0.02,
        'gdp_growth': 0.025,
        'unemployment_rate': 0.045,
        'interest_rate': 0.035,
        'inflation_rate': 0.02,
        'market_volatility': 0.15
    }


@pytest.fixture
def credit_application():
    """Initialized CreditApplication instance."""
    return CreditApplication()


@pytest.fixture
def economic_indicators():
    """Initialized EconomicIndicators instance."""
    return EconomicIndicators()


@pytest.fixture
def credit_app_with_data(credit_application, sample_economic_data):
    """CreditApplication with economic data loaded."""
    credit_application.economic_indicators.update_indicators(sample_economic_data)
    return credit_application