"""Tests for economic indicators and stress testing."""

import pytest
from credit_risk.core.economic import EconomicIndicators, STRESS_SCENARIOS


class TestEconomicIndicators:
    """Test suite for EconomicIndicators class."""

    def test_initialization(self):
        """Test EconomicIndicators initialization."""
        economic = EconomicIndicators()
        assert isinstance(economic.indicators, dict)
        assert 'gdp_growth' in economic.indicators
        assert 'unemployment_rate' in economic.indicators
        assert 'inflation_rate' in economic.indicators

    def test_update_indicators(self, economic_indicators, sample_economic_data):
        """Test updating economic indicators."""
        initial_gdp = economic_indicators.indicators['gdp_growth']
        economic_indicators.update_indicators(sample_economic_data)
        
        assert economic_indicators.indicators['gdp_growth'] == sample_economic_data['gdp_growth']
        assert economic_indicators.indicators['unemployment_rate'] == sample_economic_data['unemployment_rate']
        assert economic_indicators.indicators['inflation_rate'] == sample_economic_data['inflation_rate']

    def test_calculate_economic_risk_factor_individual(self, economic_indicators):
        """Test economic risk factor calculation for individuals."""
        risk_factor = economic_indicators.calculate_economic_risk_factor('individual')
        
        assert isinstance(risk_factor, float)
        assert 0 <= risk_factor <= 1

    def test_calculate_economic_risk_factor_corporate(self, economic_indicators):
        """Test economic risk factor calculation for corporates."""
        risk_factor = economic_indicators.calculate_economic_risk_factor('corporate', 'technology')
        
        assert isinstance(risk_factor, float)
        assert 0 <= risk_factor <= 1

    def test_apply_stress_scenario(self, economic_indicators):
        """Test applying stress scenarios."""
        original_unemployment = economic_indicators.indicators['unemployment_rate']
        
        result = economic_indicators.apply_stress_scenario('recession')
        
        assert 'scenario' in result
        assert 'original_indicators' in result
        assert 'stressed_indicators' in result
        
        # Check that unemployment increased during recession
        assert economic_indicators.indicators['unemployment_rate'] > original_unemployment

    def test_apply_invalid_stress_scenario(self, economic_indicators):
        """Test applying invalid stress scenario."""
        with pytest.raises(ValueError, match="Unknown stress scenario"):
            economic_indicators.apply_stress_scenario('invalid_scenario')

    def test_run_stress_test(self, economic_indicators, sample_individual_application):
        """Test running comprehensive stress tests."""
        stress_results = economic_indicators.run_stress_test(
            sample_individual_application, 'individual'
        )
        
        assert 'baseline_risk_factor' in stress_results
        assert 'stress_test_results' in stress_results
        assert 'worst_case_scenario' in stress_results
        assert 'best_case_scenario' in stress_results
        
        # Check that all scenarios were tested
        assert len(stress_results['stress_test_results']) == len(STRESS_SCENARIOS)
        
        # Verify scenario results structure
        for scenario_name, scenario_result in stress_results['stress_test_results'].items():
            assert 'scenario_info' in scenario_result
            assert 'baseline_risk_factor' in scenario_result
            assert 'stressed_risk_factor' in scenario_result
            assert 'risk_change' in scenario_result
            assert 'risk_change_percent' in scenario_result

    def test_get_available_stress_scenarios(self, economic_indicators):
        """Test getting available stress scenarios."""
        scenarios = economic_indicators.get_available_stress_scenarios()
        
        assert isinstance(scenarios, list)
        assert len(scenarios) == len(STRESS_SCENARIOS)
        
        for scenario in scenarios:
            assert 'name' in scenario
            assert 'title' in scenario
            assert 'description' in scenario

    def test_economic_weights_individual(self, economic_indicators):
        """Test economic weights for individuals."""
        weights = economic_indicators._get_economic_weights('individual')
        
        assert isinstance(weights, dict)
        assert 'unemployment_rate' in weights
        assert 'gdp_growth' in weights
        assert 'interest_rate' in weights
        
        # Weights should sum to approximately 1.0
        total_weight = sum(weights.values())
        assert 0.95 <= total_weight <= 1.05

    def test_economic_weights_corporate(self, economic_indicators):
        """Test economic weights for corporates."""
        weights = economic_indicators._get_economic_weights('corporate')
        
        assert isinstance(weights, dict)
        assert 'gdp_growth' in weights
        assert 'industry_growth' in weights
        assert 'market_volatility' in weights
        
        # Weights should sum to approximately 1.0
        total_weight = sum(weights.values())
        assert 0.95 <= total_weight <= 1.05

    def test_stress_scenarios_content(self):
        """Test stress scenarios have required content."""
        for scenario_name, scenario in STRESS_SCENARIOS.items():
            assert 'name' in scenario
            assert 'description' in scenario
            assert 'adjustments' in scenario
            assert isinstance(scenario['adjustments'], dict)
            
            # Check that adjustments contain numeric values
            for indicator, value in scenario['adjustments'].items():
                assert isinstance(value, (int, float))

    def test_indicator_restoration_after_stress(self, economic_indicators, sample_economic_data):
        """Test that original indicators are restored after stress testing."""
        economic_indicators.update_indicators(sample_economic_data)
        original_gdp = economic_indicators.indicators['gdp_growth']
        
        # Run stress test which should restore indicators
        economic_indicators.run_stress_test({'industry': 'technology'}, 'corporate')
        
        # Check that original values are restored
        assert economic_indicators.indicators['gdp_growth'] == original_gdp

    def test_industry_specific_risk(self, economic_indicators):
        """Test industry-specific risk calculation."""
        # Set some industry growth data
        economic_indicators.indicators['industry_growth'] = {
            'technology': 0.05,
            'retail': -0.02
        }
        
        tech_risk = economic_indicators.calculate_economic_risk_factor('corporate', 'technology')
        retail_risk = economic_indicators.calculate_economic_risk_factor('corporate', 'retail')
        
        # Retail should have higher risk due to negative growth
        assert retail_risk > tech_risk