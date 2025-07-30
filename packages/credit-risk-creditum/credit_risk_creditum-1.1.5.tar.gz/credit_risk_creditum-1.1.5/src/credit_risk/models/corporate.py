from typing import Dict, Any
from .base import BaseRiskAssessment
from ..core.economic import EconomicIndicators

class CorporateRiskAssessment(BaseRiskAssessment):
    """Handle corporate credit risk assessment"""
    
    def __init__(self, economic_indicators: EconomicIndicators):
        super().__init__(economic_indicators)
        self.weights = {
            'financial_ratios': 0.25,
            'market_position': 0.20,
            'operational_efficiency': 0.15,
            'management_quality': 0.15,
            'business_model': 0.15,
            'regulatory_compliance': 0.10
        }
    
    def calculate_risk_score(self, features: Dict[str, Any]) -> float:
        """Calculate corporate risk score with economic factors"""
        # Transform application data to risk factors
        risk_factors = self._transform_features_to_risk_factors(features)
        
        # Calculate base risk score
        base_score = sum(risk_factors.get(k, 0.5) * v for k, v in self.weights.items())
        
        # Apply economic factors
        economic_factor = self.economic_indicators.calculate_economic_risk_factor(
            'corporate', 
            industry=features.get('industry')
        )
        final_score = base_score + (economic_factor * 0.4)  # Economic risk adds to total risk
        
        return min(max(final_score, 0), 1)
    
    def _transform_features_to_risk_factors(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Transform application features to risk factor scores (0-1 scale)"""
        risk_factors = {}
        
        # Years in business (newer businesses are riskier)
        years_in_business = features.get('years_in_business', 0)
        if years_in_business < 2:
            risk_factors['business_model'] = 0.8
        elif years_in_business < 5:
            risk_factors['business_model'] = 0.5
        else:
            risk_factors['business_model'] = 0.2
        
        # Annual revenue to financial ratios (lower revenue = higher risk)
        annual_revenue = features.get('annual_revenue', 0)
        if annual_revenue < 100000:
            risk_factors['financial_ratios'] = 0.9
        elif annual_revenue < 500000:
            risk_factors['financial_ratios'] = 0.6
        elif annual_revenue < 1000000:
            risk_factors['financial_ratios'] = 0.4
        else:
            risk_factors['financial_ratios'] = 0.2
        
        # Industry-based market position risk
        industry = features.get('industry', '').lower()
        high_risk_industries = ['hospitality', 'retail', 'food_service']
        medium_risk_industries = ['manufacturing', 'construction', 'transportation']
        
        if industry in high_risk_industries:
            risk_factors['market_position'] = 0.7
        elif industry in medium_risk_industries:
            risk_factors['market_position'] = 0.5
        else:
            risk_factors['market_position'] = 0.3  # Technology, finance, healthcare
        
        # Default values for other factors (could be enhanced with more data)
        risk_factors['operational_efficiency'] = 0.4
        risk_factors['management_quality'] = 0.3
        risk_factors['regulatory_compliance'] = 0.2
        
        return risk_factors