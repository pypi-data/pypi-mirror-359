"""Tests for risk assessment models."""

import pytest
from credit_risk.models.individual import IndividualRiskAssessment
from credit_risk.models.corporate import CorporateRiskAssessment
from credit_risk.models.base import BaseRiskAssessment
from credit_risk.core.economic import EconomicIndicators


class TestIndividualRiskAssessment:
    """Test suite for IndividualRiskAssessment class."""

    @pytest.fixture
    def individual_model(self, economic_indicators):
        """Create IndividualRiskAssessment instance."""
        return IndividualRiskAssessment(economic_indicators)

    def test_initialization(self, individual_model):
        """Test IndividualRiskAssessment initialization."""
        assert isinstance(individual_model.weights, dict)
        assert 'payment_history' in individual_model.weights
        assert 'credit_utilization' in individual_model.weights
        assert 'debt_to_income' in individual_model.weights
        
        # Weights should sum to 1.0
        total_weight = sum(individual_model.weights.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_calculate_risk_score(self, individual_model, sample_individual_application):
        """Test individual risk score calculation."""
        risk_score = individual_model.calculate_risk_score(sample_individual_application)
        
        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 1

    def test_transform_features_good_credit(self, individual_model):
        """Test feature transformation for good credit applicant."""
        good_application = {
            'credit_score': 800,
            'monthly_income': 8000,
            'monthly_debt': 1000,
            'loan_amount': 20000,
            'loan_purpose': 'home_improvement'
        }
        
        risk_factors = individual_model._transform_features_to_risk_factors(good_application)
        
        # Good credit should have low risk factors
        assert risk_factors['payment_history'] < 0.3
        assert risk_factors['debt_to_income'] < 0.5

    def test_transform_features_poor_credit(self, individual_model):
        """Test feature transformation for poor credit applicant."""
        poor_application = {
            'credit_score': 550,
            'monthly_income': 2000,
            'monthly_debt': 1500,
            'loan_amount': 25000,
            'loan_purpose': 'debt_consolidation'
        }
        
        risk_factors = individual_model._transform_features_to_risk_factors(poor_application)
        
        # Poor credit should have higher risk factors
        assert risk_factors['payment_history'] > 0.5
        assert risk_factors['debt_to_income'] > 0.8

    def test_dti_edge_cases(self, individual_model):
        """Test debt-to-income ratio edge cases."""
        # Zero income
        zero_income_app = {
            'credit_score': 720,
            'monthly_income': 0,
            'monthly_debt': 1500,
            'loan_amount': 20000,
            'loan_purpose': 'personal'
        }
        risk_factors = individual_model._transform_features_to_risk_factors(zero_income_app)
        assert risk_factors['debt_to_income'] == 1.0

        # Very high income
        high_income_app = {
            'credit_score': 720,
            'monthly_income': 20000,
            'monthly_debt': 1000,
            'loan_amount': 20000,
            'loan_purpose': 'personal'
        }
        risk_factors = individual_model._transform_features_to_risk_factors(high_income_app)
        assert risk_factors['debt_to_income'] < 0.2


class TestCorporateRiskAssessment:
    """Test suite for CorporateRiskAssessment class."""

    @pytest.fixture
    def corporate_model(self, economic_indicators):
        """Create CorporateRiskAssessment instance."""
        return CorporateRiskAssessment(economic_indicators)

    def test_initialization(self, corporate_model):
        """Test CorporateRiskAssessment initialization."""
        assert isinstance(corporate_model.weights, dict)
        assert 'financial_ratios' in corporate_model.weights
        assert 'market_position' in corporate_model.weights
        assert 'business_model' in corporate_model.weights
        
        # Weights should sum to 1.0
        total_weight = sum(corporate_model.weights.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_calculate_risk_score(self, corporate_model, sample_corporate_application):
        """Test corporate risk score calculation."""
        risk_score = corporate_model.calculate_risk_score(sample_corporate_application)
        
        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 1

    def test_transform_features_established_business(self, corporate_model):
        """Test feature transformation for established business."""
        established_corp = {
            'years_in_business': 10,
            'annual_revenue': 2000000,
            'industry': 'technology',
            'loan_amount': 100000,
            'loan_purpose': 'expansion'
        }
        
        risk_factors = corporate_model._transform_features_to_risk_factors(established_corp)
        
        # Established business should have lower risk
        assert risk_factors['business_model'] < 0.4
        assert risk_factors['financial_ratios'] < 0.4

    def test_transform_features_startup(self, corporate_model):
        """Test feature transformation for startup business."""
        startup_corp = {
            'years_in_business': 1,
            'annual_revenue': 50000,
            'industry': 'retail',
            'loan_amount': 50000,
            'loan_purpose': 'equipment'
        }
        
        risk_factors = corporate_model._transform_features_to_risk_factors(startup_corp)
        
        # Startup should have higher risk
        assert risk_factors['business_model'] > 0.7
        assert risk_factors['financial_ratios'] > 0.8

    def test_industry_risk_assessment(self, corporate_model):
        """Test industry-based risk assessment."""
        # Technology (low risk)
        tech_corp = {
            'years_in_business': 5,
            'annual_revenue': 500000,
            'industry': 'technology',
            'loan_amount': 100000,
            'loan_purpose': 'expansion'
        }
        
        # Retail (high risk)
        retail_corp = {
            'years_in_business': 5,
            'annual_revenue': 500000,
            'industry': 'retail',
            'loan_amount': 100000,
            'loan_purpose': 'expansion'
        }
        
        tech_factors = corporate_model._transform_features_to_risk_factors(tech_corp)
        retail_factors = corporate_model._transform_features_to_risk_factors(retail_corp)
        
        # Retail should have higher market position risk
        assert retail_factors['market_position'] > tech_factors['market_position']

    def test_revenue_thresholds(self, corporate_model):
        """Test revenue-based risk thresholds."""
        revenues = [50000, 250000, 750000, 1500000]
        risk_scores = []
        
        for revenue in revenues:
            corp = {
                'years_in_business': 5,
                'annual_revenue': revenue,
                'industry': 'technology',
                'loan_amount': 100000,
                'loan_purpose': 'expansion'
            }
            factors = corporate_model._transform_features_to_risk_factors(corp)
            risk_scores.append(factors['financial_ratios'])
        
        # Risk should decrease as revenue increases
        for i in range(1, len(risk_scores)):
            assert risk_scores[i] <= risk_scores[i-1]


class TestBaseRiskAssessment:
    """Test suite for BaseRiskAssessment class."""

    @pytest.fixture
    def base_model(self, economic_indicators):
        """Create BaseRiskAssessment instance."""
        return BaseRiskAssessment(economic_indicators)

    def test_initialization(self, base_model):
        """Test BaseRiskAssessment initialization."""
        assert base_model.economic_indicators is not None
        assert base_model.scaler is not None
        assert base_model.model is None
        assert isinstance(base_model.risk_thresholds, dict)
        
        # Check risk thresholds
        assert 'low' in base_model.risk_thresholds
        assert 'medium' in base_model.risk_thresholds
        assert 'high' in base_model.risk_thresholds

    def test_risk_thresholds_ordering(self, base_model):
        """Test that risk thresholds are properly ordered."""
        thresholds = base_model.risk_thresholds
        assert thresholds['low'] < thresholds['medium']
        assert thresholds['medium'] < thresholds['high']

    def test_predict_risk_without_model(self, base_model):
        """Test that predict_risk raises error without trained model."""
        import numpy as np
        
        with pytest.raises(ValueError, match="Model not trained"):
            base_model.predict_risk(np.array([[1, 2, 3]]))

    # Note: Testing train_model and preprocess_data would require actual data
    # which is beyond the scope of unit tests. These would be better tested
    # in integration tests with sample datasets.