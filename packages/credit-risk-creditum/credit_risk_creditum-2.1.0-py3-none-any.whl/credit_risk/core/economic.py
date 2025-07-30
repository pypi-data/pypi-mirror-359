from typing import Dict, Any, Optional, List
import copy

# Predefined stress testing scenarios
STRESS_SCENARIOS = {
    'recession': {
        'name': 'Economic Recession',
        'description': 'Simulates recession conditions with high unemployment and negative GDP growth',
        'adjustments': {
            'unemployment_rate': 0.08,  # 8% unemployment
            'gdp_growth': -0.02,        # -2% GDP growth
            'interest_rate': 0.02,      # 2% interest rate (low)
            'inflation_rate': 0.01,     # 1% inflation (low)
            'market_volatility': 0.35   # 35% volatility (high)
        }
    },
    'inflation_surge': {
        'name': 'High Inflation Period',
        'description': 'Simulates high inflation environment with rising interest rates',
        'adjustments': {
            'inflation_rate': 0.06,     # 6% inflation
            'interest_rate': 0.07,      # 7% interest rate
            'cpi': 0.06,               # 6% CPI growth
            'market_volatility': 0.25   # 25% volatility
        }
    },
    'market_crash': {
        'name': 'Market Volatility Crisis',
        'description': 'Simulates extreme market volatility and uncertainty',
        'adjustments': {
            'market_volatility': 0.50,  # 50% volatility (extreme)
            'gdp_growth': -0.01,        # -1% GDP growth
            'unemployment_rate': 0.06,  # 6% unemployment
            'interest_rate': 0.01       # 1% emergency low rates
        }
    },
    'optimistic': {
        'name': 'Economic Boom',
        'description': 'Simulates strong economic growth conditions',
        'adjustments': {
            'gdp_growth': 0.04,         # 4% GDP growth
            'unemployment_rate': 0.03,  # 3% unemployment (low)
            'inflation_rate': 0.02,     # 2% inflation (target)
            'interest_rate': 0.04,      # 4% interest rate
            'market_volatility': 0.12   # 12% volatility (low)
        }
    }
}


class EconomicIndicators:
    """
    Handle economic indicators and their impact on credit risk assessment.

    This class manages various economic indicators such as CPI, GDP growth,
    unemployment rate, etc., and calculates their impact on credit risk.

    Attributes:
        indicators (dict): Dictionary storing current economic indicators.
    """

    def __init__(self):
        """Initialize economic indicators with default values."""
        self.indicators = {
            'cpi': 0.02,
            'gdp_growth': 0.025,
            'unemployment_rate': 0.045,
            'interest_rate': 0.035,
            'inflation_rate': 0.02,
            'industry_growth': {},
            'market_volatility': 0.15,
            'currency_stability': 0.8,
            'housing_price_index': 0.03
        }
        
    def update_indicators(self, indicator_data: Dict[str, Any]) -> None:
        """
        Update economic indicators with current data.

        Args:
            indicator_data (Dict[str, Any]): Dictionary containing economic indicators.
                Expected keys:
                - cpi (float): Consumer Price Index
                - gdp_growth (float): GDP growth rate
                - unemployment_rate (float): Unemployment rate
                - interest_rate (float): Current interest rate
                - inflation_rate (float): Inflation rate
                - industry_growth (Dict[str, float]): Growth rates by industry
                - market_volatility (float): Market volatility index
                - currency_stability (float): Currency stability index

        Example:
            >>> economic = EconomicIndicators()
            >>> data = {
            ...     'cpi': 0.02,
            ...     'gdp_growth': 0.03,
            ...     'unemployment_rate': 0.05
            ... }
            >>> economic.update_indicators(data)
        """
        for key, value in indicator_data.items():
            if key in self.indicators or key == 'industry_growth':
                self.indicators[key] = value
    
    def calculate_economic_risk_factor(self, entity_type: str = 'individual', 
                                     industry: Optional[str] = None) -> float:
        """
        Calculate economic risk factor based on entity type and industry.
        
        Args:
            entity_type (str): Type of entity ('individual' or 'corporate')
            industry (str, optional): Industry sector for corporate entities
            
        Returns:
            float: Economic risk factor between 0 and 1 (1 = highest risk)
        """
        weights = self._get_economic_weights(entity_type)
        
        risk_factor = 0.0
        for indicator, weight in weights.items():
            if indicator == 'industry_growth' and industry:
                # Use industry-specific growth rate if available
                industry_growth = self.indicators.get('industry_growth', {})
                value = industry_growth.get(industry, 0.0)  # Default to neutral
                # Convert growth rate to risk (negative growth = higher risk)
                value = max(0, -value + 0.5)  # Transform to 0-1 risk scale
            else:
                value = self.indicators.get(indicator, 0.5)  # Default to neutral
                
                # Transform some indicators to risk scale
                if indicator == 'gdp_growth':
                    # Negative growth = higher risk
                    value = max(0, -value + 0.5)
                elif indicator in ['unemployment_rate', 'inflation_rate', 'market_volatility']:
                    # Higher values = higher risk (already in right direction)
                    pass
                elif indicator == 'interest_rate':
                    # Both very high and very low rates can indicate risk
                    optimal_rate = 0.04  # 4% is often considered optimal
                    value = abs(value - optimal_rate) / optimal_rate
                    
            risk_factor += value * weight
            
        return min(max(risk_factor, 0), 1)
    
    def apply_stress_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Apply a predefined stress testing scenario to economic indicators.
        
        Args:
            scenario_name (str): Name of the stress scenario to apply.
                Available scenarios: 'recession', 'inflation_surge', 
                'market_crash', 'optimistic'
        
        Returns:
            Dict[str, Any]: Updated economic indicators with stress adjustments
            
        Example:
            >>> economic = EconomicIndicators()
            >>> stressed_indicators = economic.apply_stress_scenario('recession')
            >>> # Economic indicators now reflect recession conditions
        """
        if scenario_name not in STRESS_SCENARIOS:
            raise ValueError(f"Unknown stress scenario: {scenario_name}. "
                           f"Available scenarios: {list(STRESS_SCENARIOS.keys())}")
        
        scenario = STRESS_SCENARIOS[scenario_name]
        original_indicators = copy.deepcopy(self.indicators)
        
        # Apply stress adjustments
        for indicator, value in scenario['adjustments'].items():
            self.indicators[indicator] = value
        
        return {
            'scenario': scenario,
            'original_indicators': original_indicators,
            'stressed_indicators': copy.deepcopy(self.indicators)
        }
    
    def run_stress_test(self, application_data: Dict[str, Any], 
                       entity_type: str = 'individual') -> Dict[str, Any]:
        """
        Run stress tests across all scenarios for given application.
        
        Args:
            application_data (Dict[str, Any]): Credit application data
            entity_type (str): Type of entity ('individual' or 'corporate')
            
        Returns:
            Dict[str, Any]: Stress test results for all scenarios
            
        Example:
            >>> economic = EconomicIndicators()
            >>> app_data = {'credit_score': 720, 'monthly_income': 5000}
            >>> stress_results = economic.run_stress_test(app_data, 'individual')
        """
        original_indicators = copy.deepcopy(self.indicators)
        stress_results = {}
        
        # Calculate baseline risk factor
        baseline_risk = self.calculate_economic_risk_factor(entity_type, 
                                                          application_data.get('industry'))
        
        for scenario_name, scenario in STRESS_SCENARIOS.items():
            # Apply stress scenario
            self.apply_stress_scenario(scenario_name)
            
            # Calculate stressed risk factor
            stressed_risk = self.calculate_economic_risk_factor(entity_type,
                                                              application_data.get('industry'))
            
            stress_results[scenario_name] = {
                'scenario_info': scenario,
                'baseline_risk_factor': baseline_risk,
                'stressed_risk_factor': stressed_risk,
                'risk_change': stressed_risk - baseline_risk,
                'risk_change_percent': ((stressed_risk - baseline_risk) / baseline_risk * 100) if baseline_risk > 0 else 0
            }
        
        # Restore original indicators
        self.indicators = original_indicators
        
        return {
            'baseline_risk_factor': baseline_risk,
            'stress_test_results': stress_results,
            'worst_case_scenario': max(stress_results.keys(), 
                                     key=lambda x: stress_results[x]['stressed_risk_factor']),
            'best_case_scenario': min(stress_results.keys(),
                                    key=lambda x: stress_results[x]['stressed_risk_factor'])
        }
    
    def get_available_stress_scenarios(self) -> List[Dict[str, str]]:
        """
        Get list of available stress testing scenarios.
        
        Returns:
            List[Dict[str, str]]: List of available scenarios with descriptions
        """
        return [
            {
                'name': name,
                'title': scenario['name'],
                'description': scenario['description']
            }
            for name, scenario in STRESS_SCENARIOS.items()
        ]

    def _get_economic_weights(self, entity_type: str) -> Dict[str, float]:
        """Get economic factor weights based on entity type."""
        if entity_type == 'individual':
            return {
                'cpi': 0.16,
                'unemployment_rate': 0.26,
                'interest_rate': 0.21,
                'inflation_rate': 0.11,
                'housing_price_index': 0.05,
                'market_volatility': 0.02,
                'gdp_growth': 0.19
            }
        return {
            'gdp_growth': 0.25,
            'industry_growth': 0.20,
            'interest_rate': 0.20,
            'market_volatility': 0.15,
            'unemployment_rate': 0.10,
            'inflation_rate': 0.10
        }