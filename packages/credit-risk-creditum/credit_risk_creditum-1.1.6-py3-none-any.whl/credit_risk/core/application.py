import numpy as np
from typing import Dict, Any, Tuple

from ..core.economic import EconomicIndicators
from ..models.individual import IndividualRiskAssessment
from ..models.corporate import CorporateRiskAssessment

class CreditApplication:
    """Handle credit applications and make approval decisions"""
    
    def __init__(self, min_credit_score: int = 600, max_dti: float = 0.43):
        self.min_credit_score = min_credit_score
        self.max_dti = max_dti
        self.economic_indicators = EconomicIndicators()
        self.individual_assessment = IndividualRiskAssessment(self.economic_indicators)
        self.corporate_assessment = CorporateRiskAssessment(self.economic_indicators)
    
    def validate_application(self, application_data: Dict[str, Any], 
                           entity_type: str = 'individual') -> Tuple[bool, str]:
        """Validate credit application data"""
        required_fields = self._get_required_fields(entity_type)
        
        for field in required_fields:
            if field not in application_data:
                return False, f"Missing required field: {field}"
        
        if entity_type == 'individual':
            return self._validate_individual(application_data)
        return self._validate_corporate(application_data)
    
    def _validate_individual(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate individual application"""
        if data['credit_score'] < self.min_credit_score:
            return False, "Credit score below minimum requirement"
        
        dti = self._calculate_dti(data['monthly_debt'], data['monthly_income'])
        if dti > self.max_dti:
            return False, "Debt-to-income ratio too high"
        
        return True, "Application valid"
    
    def _validate_corporate(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate corporate application"""
        if data['years_in_business'] < 2:
            return False, "Minimum 2 years in business required"
        
        if data['annual_revenue'] < 100000:
            return False, "Minimum annual revenue requirement not met"
        
        return True, "Application valid"
    
    @staticmethod
    def _get_required_fields(entity_type: str) -> list:
        """Get required fields based on entity type"""
        if entity_type == 'individual':
            return [
                'credit_score',
                'monthly_income',
                'monthly_debt',
                'loan_amount',
                'loan_purpose'
            ]
        return [
            'years_in_business',
            'annual_revenue',
            'industry',
            'loan_amount',
            'loan_purpose'
        ]
    
    @staticmethod
    def _calculate_dti(monthly_debt: float, monthly_income: float) -> float:
        """Calculate Debt-to-Income ratio"""
        if monthly_income <= 0:
            return float('inf')
        return monthly_debt / monthly_income
    
    def make_decision(self, application_data: Dict[str, Any], 
                     entity_type: str = 'individual',
                     stress_scenario: str = None) -> Dict[str, Any]:
        """Make credit approval decision with optional stress testing"""
        is_valid, message = self.validate_application(application_data, entity_type)
        if not is_valid:
            return {
                'decision': 'rejected',
                'reason': message,
                'risk_score': 1.0,  # Maximum risk score for rejected applications
                'risk_category': 'high',
                'max_loan_amount': 0,
                'economic_factor': self.economic_indicators.calculate_economic_risk_factor(
                    entity_type,
                    industry=application_data.get('industry')
                )
            }
        
        # Apply stress scenario if specified
        original_indicators = None
        if stress_scenario:
            original_indicators = self.economic_indicators.indicators.copy()
            self.economic_indicators.apply_stress_scenario(stress_scenario)
        
        try:
            # Calculate risk score based on entity type
            if entity_type == 'individual':
                risk_score = self.individual_assessment.calculate_risk_score(application_data)
                assessor = self.individual_assessment
            else:
                risk_score = self.corporate_assessment.calculate_risk_score(application_data)
                assessor = self.corporate_assessment
            
            risk_category = self._get_risk_category(risk_score)
            
            result = {
                'decision': 'approved' if risk_category != 'high' else 'rejected',
                'risk_score': risk_score,
                'risk_category': risk_category,
                'max_loan_amount': self._calculate_max_loan_amount(
                    application_data,
                    risk_score,
                    entity_type
                ) if risk_category != 'high' else 0,
                'economic_factor': self.economic_indicators.calculate_economic_risk_factor(
                    entity_type,
                    industry=application_data.get('industry')
                )
            }
            
            if stress_scenario:
                result['stress_scenario'] = stress_scenario
                
            return result
            
        finally:
            # Restore original indicators if stress testing was applied
            if original_indicators is not None:
                self.economic_indicators.indicators = original_indicators
    
    def _calculate_max_loan_amount(self, application_data: Dict[str, Any],
                                risk_score: float, entity_type: str) -> float:
        """Calculate maximum loan amount"""
        if entity_type == 'individual':
            base_max = application_data['monthly_income'] * 36
        else:
            base_max = application_data['annual_revenue'] * 0.5
        
        risk_multiplier = 1 - risk_score
        return base_max * risk_multiplier
    
    def run_stress_tests(self, application_data: Dict[str, Any], 
                        entity_type: str = 'individual') -> Dict[str, Any]:
        """
        Run comprehensive stress tests on credit application.
        
        Args:
            application_data (Dict[str, Any]): Credit application data
            entity_type (str): Type of entity ('individual' or 'corporate')
            
        Returns:
            Dict[str, Any]: Comprehensive stress test results
        """
        # Get baseline decision
        baseline_decision = self.make_decision(application_data, entity_type)
        
        # Run economic stress tests
        economic_stress_results = self.economic_indicators.run_stress_test(
            application_data, entity_type
        )
        
        # Test each stress scenario
        scenario_results = {}
        for scenario_name in self.economic_indicators.get_available_stress_scenarios():
            scenario_decision = self.make_decision(
                application_data, entity_type, scenario_name['name']
            )
            scenario_results[scenario_name['name']] = {
                'scenario_info': scenario_name,
                'decision': scenario_decision,
                'decision_change': scenario_decision['decision'] != baseline_decision['decision'],
                'risk_score_change': (scenario_decision['risk_score'] or 0) - (baseline_decision['risk_score'] or 0)
            }
        
        return {
            'baseline_decision': baseline_decision,
            'economic_stress_results': economic_stress_results,
            'scenario_results': scenario_results,
            'summary': {
                'decision_changes': sum(1 for r in scenario_results.values() if r['decision_change']),
                'worst_case_risk_score': max((r['decision']['risk_score'] or 0) for r in scenario_results.values()),
                'best_case_risk_score': min((r['decision']['risk_score'] or 0) for r in scenario_results.values()),
                'stable_decision': all(not r['decision_change'] for r in scenario_results.values())
            }
        }
    
    def get_stress_scenarios(self) -> list:
        """Get available stress testing scenarios"""
        return self.economic_indicators.get_available_stress_scenarios()

    def _get_risk_category(self, risk_score: float) -> str:
        """Determine risk category based on risk score"""
        if risk_score <= 0.3:
            return 'low'
        elif risk_score <= 0.6:
            return 'medium'
        return 'high'