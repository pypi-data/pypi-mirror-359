from typing import Dict, Any
from .base import BaseRiskAssessment
from ..core.economic import EconomicIndicators

class IndividualRiskAssessment(BaseRiskAssessment):
    """Handle individual credit risk assessment"""
    
    def __init__(self, economic_indicators: EconomicIndicators):
        super().__init__(economic_indicators)
        self.weights = {
            'payment_history': 0.30,
            'credit_utilization': 0.25,
            'credit_history_length': 0.15,
            'income_stability': 0.15,
            'debt_to_income': 0.15
        }
    
    def calculate_risk_score(self, features: Dict[str, Any]) -> float:
        """Calculate individual risk score with economic factors"""
        # Transform application data to risk factors
        risk_factors = self._transform_features_to_risk_factors(features)
        
        # Calculate base risk score
        base_score = sum(risk_factors.get(k, 0.5) * v for k, v in self.weights.items())
        
        # Apply economic factors
        economic_factor = self.economic_indicators.calculate_economic_risk_factor('individual')
        final_score = base_score + (economic_factor * 0.3)  # Economic risk adds to total risk
        
        return min(max(final_score, 0), 1)
    
    def _transform_features_to_risk_factors(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Transform application features to risk factor scores (0-1 scale)"""
        risk_factors = {}
        
        # Credit score to payment history risk (higher credit score = lower risk)
        credit_score = features.get('credit_score', 600)
        risk_factors['payment_history'] = max(0, (850 - credit_score) / (850 - 300))
        
        # Debt-to-income ratio risk
        monthly_income = features.get('monthly_income', 1)
        monthly_debt = features.get('monthly_debt', 0)
        dti = monthly_debt / monthly_income if monthly_income > 0 else 1.0
        risk_factors['debt_to_income'] = min(1.0, dti / 0.5)  # Risk increases as DTI approaches 50%
        
        # Credit utilization (estimate based on debt level)
        # Higher debt relative to income suggests higher utilization
        risk_factors['credit_utilization'] = min(1.0, dti * 1.5)
        
        # Income stability (assume stable if income > certain threshold)
        risk_factors['income_stability'] = max(0, (3000 - monthly_income) / 3000) if monthly_income < 3000 else 0.1
        
        # Credit history length (assume average for now - could be enhanced with actual data)
        risk_factors['credit_history_length'] = 0.3  # Assume moderate risk
        
        return risk_factors