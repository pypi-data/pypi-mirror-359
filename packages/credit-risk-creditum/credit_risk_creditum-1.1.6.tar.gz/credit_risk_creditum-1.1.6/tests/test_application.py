"""Tests for credit application processing."""

import pytest
from credit_risk.core.application import CreditApplication


class TestCreditApplication:
    """Test suite for CreditApplication class."""

    def test_initialization(self):
        """Test CreditApplication initialization."""
        app = CreditApplication()
        assert app.min_credit_score == 600
        assert app.max_dti == 0.43
        assert app.economic_indicators is not None
        assert app.individual_assessment is not None
        assert app.corporate_assessment is not None

    def test_initialization_with_custom_params(self):
        """Test CreditApplication initialization with custom parameters."""
        app = CreditApplication(min_credit_score=650, max_dti=0.4)
        assert app.min_credit_score == 650
        assert app.max_dti == 0.4

    def test_individual_validation_success(self, credit_application, sample_individual_application):
        """Test successful individual application validation."""
        is_valid, message = credit_application.validate_application(
            sample_individual_application, 'individual'
        )
        assert is_valid is True
        assert message == "Application valid"

    def test_individual_validation_low_credit_score(self, credit_application):
        """Test individual validation with low credit score."""
        application = {
            'credit_score': 500,
            'monthly_income': 5000,
            'monthly_debt': 1500,
            'loan_amount': 25000,
            'loan_purpose': 'home_improvement'
        }
        is_valid, message = credit_application.validate_application(application, 'individual')
        assert is_valid is False
        assert "Credit score below minimum requirement" in message

    def test_individual_validation_high_dti(self, credit_application):
        """Test individual validation with high debt-to-income ratio."""
        application = {
            'credit_score': 720,
            'monthly_income': 3000,
            'monthly_debt': 1500,  # DTI = 0.5 > 0.43
            'loan_amount': 25000,
            'loan_purpose': 'home_improvement'
        }
        is_valid, message = credit_application.validate_application(application, 'individual')
        assert is_valid is False
        assert "Debt-to-income ratio too high" in message

    def test_individual_validation_missing_fields(self, credit_application):
        """Test individual validation with missing required fields."""
        application = {
            'credit_score': 720,
            'monthly_income': 5000
            # Missing other required fields
        }
        is_valid, message = credit_application.validate_application(application, 'individual')
        assert is_valid is False
        assert "Missing required field" in message

    def test_corporate_validation_success(self, credit_application, sample_corporate_application):
        """Test successful corporate application validation."""
        is_valid, message = credit_application.validate_application(
            sample_corporate_application, 'corporate'
        )
        assert is_valid is True
        assert message == "Application valid"

    def test_corporate_validation_insufficient_years(self, credit_application):
        """Test corporate validation with insufficient years in business."""
        application = {
            'years_in_business': 1,
            'annual_revenue': 500000,
            'industry': 'technology',
            'loan_amount': 100000,
            'loan_purpose': 'expansion'
        }
        is_valid, message = credit_application.validate_application(application, 'corporate')
        assert is_valid is False
        assert "Minimum 2 years in business required" in message

    def test_corporate_validation_low_revenue(self, credit_application):
        """Test corporate validation with low annual revenue."""
        application = {
            'years_in_business': 5,
            'annual_revenue': 50000,
            'industry': 'technology',
            'loan_amount': 100000,
            'loan_purpose': 'expansion'
        }
        is_valid, message = credit_application.validate_application(application, 'corporate')
        assert is_valid is False
        assert "Minimum annual revenue requirement not met" in message

    def test_individual_decision_approved(self, credit_app_with_data, sample_individual_application):
        """Test individual application gets approved."""
        decision = credit_app_with_data.make_decision(sample_individual_application, 'individual')
        
        assert decision['decision'] == 'approved'
        assert 'risk_score' in decision
        assert 'risk_category' in decision
        assert 'max_loan_amount' in decision
        assert decision['risk_score'] >= 0.0
        assert decision['risk_score'] <= 1.0

    def test_corporate_decision_approved(self, credit_app_with_data, sample_corporate_application):
        """Test corporate application gets approved."""
        decision = credit_app_with_data.make_decision(sample_corporate_application, 'corporate')
        
        assert decision['decision'] == 'approved'
        assert 'risk_score' in decision
        assert 'risk_category' in decision
        assert 'max_loan_amount' in decision
        assert decision['risk_score'] >= 0.0
        assert decision['risk_score'] <= 1.0

    def test_stress_testing(self, credit_app_with_data, sample_individual_application):
        """Test stress testing functionality."""
        stress_results = credit_app_with_data.run_stress_tests(
            sample_individual_application, 'individual'
        )
        
        assert 'baseline_decision' in stress_results
        assert 'scenario_results' in stress_results
        assert 'summary' in stress_results
        assert len(stress_results['scenario_results']) == 4  # 4 stress scenarios
        
        # Check summary statistics
        summary = stress_results['summary']
        assert 'decision_changes' in summary
        assert 'worst_case_risk_score' in summary
        assert 'best_case_risk_score' in summary
        assert 'stable_decision' in summary

    def test_calculate_dti(self):
        """Test DTI calculation."""
        dti = CreditApplication._calculate_dti(1500, 5000)
        assert dti == 0.3
        
        # Test division by zero
        dti_zero = CreditApplication._calculate_dti(1500, 0)
        assert dti_zero == float('inf')

    def test_get_required_fields(self):
        """Test required fields retrieval."""
        individual_fields = CreditApplication._get_required_fields('individual')
        corporate_fields = CreditApplication._get_required_fields('corporate')
        
        assert 'credit_score' in individual_fields
        assert 'monthly_income' in individual_fields
        assert 'years_in_business' in corporate_fields
        assert 'annual_revenue' in corporate_fields

    def test_max_loan_amount_calculation(self, credit_application):
        """Test maximum loan amount calculation."""
        # Individual
        individual_app = {
            'monthly_income': 5000,
            'credit_score': 720,
            'monthly_debt': 1500,
            'loan_amount': 25000,
            'loan_purpose': 'home_improvement'
        }
        
        max_amount = credit_application._calculate_max_loan_amount(
            individual_app, 0.3, 'individual'
        )
        expected = 5000 * 36 * (1 - 0.3)  # Base calculation with risk adjustment
        assert max_amount == expected
        
        # Corporate
        corporate_app = {
            'annual_revenue': 500000,
            'years_in_business': 5,
            'industry': 'technology',
            'loan_amount': 100000,
            'loan_purpose': 'expansion'
        }
        
        max_amount_corp = credit_application._calculate_max_loan_amount(
            corporate_app, 0.4, 'corporate'
        )
        expected_corp = 500000 * 0.5 * (1 - 0.4)
        assert max_amount_corp == expected_corp