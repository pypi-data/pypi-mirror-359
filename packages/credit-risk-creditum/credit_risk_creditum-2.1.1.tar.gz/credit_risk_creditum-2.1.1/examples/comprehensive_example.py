#!/usr/bin/env python3
"""
Comprehensive example demonstrating all features of credit-risk-creditum.

This example shows how to:
1. Assess individual and corporate credit risk
2. Run stress tests
3. Use economic indicators
4. Handle different scenarios
5. Configure the system
"""

import json
from pathlib import Path
from typing import Dict, Any

from credit_risk import CreditApplication, EconomicIndicators
from credit_risk.config import Config, get_config
from credit_risk.logging_config import setup_logging, get_logger


def setup_example():
    """Setup logging and configuration for the example."""
    setup_logging(log_level='INFO')
    logger = get_logger('example')
    logger.info("Starting comprehensive credit risk assessment example")
    return logger


def demonstrate_individual_assessment(app: CreditApplication, logger) -> Dict[str, Any]:
    """Demonstrate individual credit risk assessment."""
    logger.info("=== Individual Credit Risk Assessment ===")
    
    # Example applications with different risk profiles
    applications = {
        'excellent_credit': {
            'credit_score': 820,
            'income': 96000,  # Annual income
            'monthly_debt': 1200,
            'loan_amount': 30000,
            'loan_purpose': 'home_improvement',
            'employment_history': 'stable',
            'debt_to_income_ratio': 15.0
        },
        'good_credit': {
            'credit_score': 720,
            'income': 60000,  # Annual income
            'monthly_debt': 1500,
            'loan_amount': 25000,
            'loan_purpose': 'auto',
            'employment_history': 'stable',
            'debt_to_income_ratio': 30.0
        },
        'fair_credit': {
            'credit_score': 650,
            'income': 42000,  # Annual income
            'monthly_debt': 1400,
            'loan_amount': 15000,
            'loan_purpose': 'debt_consolidation',
            'employment_history': 'stable',
            'debt_to_income_ratio': 40.0
        },
        'poor_credit': {
            'credit_score': 580,
            'income': 33600,  # Annual income
            'monthly_debt': 1600,
            'loan_amount': 10000,
            'loan_purpose': 'personal',
            'employment_history': 'unstable',
            'debt_to_income_ratio': 57.1
        }
    }
    
    results = {}
    
    for profile_name, application in applications.items():
        logger.info(f"Assessing {profile_name} application...")
        
        decision = app.make_decision(application, 'individual')
        results[profile_name] = decision
        
        logger.info(f"  Decision: {decision['decision'].upper()}")
        logger.info(f"  Risk Score: {decision.get('risk_score', 0):.3f}")
        logger.info(f"  Risk Category: {decision.get('risk_category', 'N/A')}")
        logger.info(f"  Max Loan Amount: ${decision.get('max_loan_amount', 0):,.0f}")
        logger.info("")
    
    return results


def demonstrate_corporate_assessment(app: CreditApplication, logger) -> Dict[str, Any]:
    """Demonstrate corporate credit risk assessment."""
    logger.info("=== Corporate Credit Risk Assessment ===")
    
    # Example corporate applications
    applications = {
        'tech_startup': {
            'years_in_business': 2,
            'revenue': 150000,  # Frontend uses 'revenue'
            'industry': 'technology',
            'loan_amount': 50000,
            'loan_purpose': 'equipment',
            'business_credit_score': 45,
            'collateral_value': 25000,
            'cash_flow': 25000
        },
        'established_manufacturing': {
            'years_in_business': 15,
            'revenue': 2500000,  # Frontend uses 'revenue'
            'industry': 'manufacturing',
            'loan_amount': 500000,
            'loan_purpose': 'expansion',
            'business_credit_score': 85,
            'collateral_value': 1000000,
            'cash_flow': 400000
        },
        'retail_business': {
            'years_in_business': 8,
            'revenue': 800000,  # Frontend uses 'revenue'
            'industry': 'retail',
            'loan_amount': 200000,
            'loan_purpose': 'inventory',
            'business_credit_score': 65,
            'collateral_value': 300000,
            'cash_flow': 120000
        },
        'healthcare_practice': {
            'years_in_business': 12,
            'revenue': 1200000,  # Frontend uses 'revenue'
            'industry': 'healthcare',
            'loan_amount': 300000,
            'loan_purpose': 'facility_upgrade',
            'business_credit_score': 78,
            'collateral_value': 800000,
            'cash_flow': 200000
        }
    }
    
    results = {}
    
    for profile_name, application in applications.items():
        logger.info(f"Assessing {profile_name} application...")
        
        decision = app.make_decision(application, 'corporate')
        results[profile_name] = decision
        
        logger.info(f"  Decision: {decision['decision'].upper()}")
        logger.info(f"  Risk Score: {decision.get('risk_score', 0):.3f}")
        logger.info(f"  Risk Category: {decision.get('risk_category', 'N/A')}")
        logger.info(f"  Max Loan Amount: ${decision.get('max_loan_amount', 0):,.0f}")
        logger.info("")
    
    return results


def demonstrate_economic_scenarios(app: CreditApplication, logger):
    """Demonstrate different economic scenarios."""
    logger.info("=== Economic Scenarios Impact ===")
    
    # Base application for testing
    test_application = {
        'credit_score': 720,
        'income': 60000,  # Annual income
        'monthly_debt': 1500,
        'loan_amount': 25000,
        'loan_purpose': 'auto',
        'employment_history': 'stable',
        'debt_to_income_ratio': 30.0
    }
    
    # Different economic scenarios
    scenarios = {
        'normal_economy': {
            'gdp_growth': 0.025,
            'unemployment_rate': 0.045,
            'inflation_rate': 0.02,
            'interest_rate': 0.035,
            'market_volatility': 0.15
        },
        'recession': {
            'gdp_growth': -0.02,
            'unemployment_rate': 0.08,
            'inflation_rate': 0.01,
            'interest_rate': 0.02,
            'market_volatility': 0.35
        },
        'boom_economy': {
            'gdp_growth': 0.045,
            'unemployment_rate': 0.03,
            'inflation_rate': 0.025,
            'interest_rate': 0.045,
            'market_volatility': 0.10
        },
        'high_inflation': {
            'gdp_growth': 0.015,
            'unemployment_rate': 0.05,
            'inflation_rate': 0.06,
            'interest_rate': 0.07,
            'market_volatility': 0.25
        }
    }
    
    for scenario_name, economic_data in scenarios.items():
        logger.info(f"Testing {scenario_name} scenario...")
        
        # Update economic indicators
        app.economic_indicators.update_indicators(economic_data)
        
        # Make decision
        decision = app.make_decision(test_application, 'individual')
        
        logger.info(f"  Risk Score: {decision.get('risk_score', 0):.3f}")
        logger.info(f"  Economic Factor: {decision.get('economic_factor', 0):.3f}")
        logger.info(f"  Decision: {decision['decision'].upper()}")
        logger.info("")


def demonstrate_stress_testing(app: CreditApplication, logger):
    """Demonstrate comprehensive stress testing."""
    logger.info("=== Stress Testing ===")
    
    # Test applications
    applications = {
        'individual': {
            'credit_score': 720,
            'income': 60000,  # Annual income
            'monthly_debt': 1500,
            'loan_amount': 25000,
            'loan_purpose': 'auto',
            'employment_history': 'stable',
            'debt_to_income_ratio': 30.0
        },
        'corporate': {
            'years_in_business': 5,
            'revenue': 500000,  # Frontend uses 'revenue'
            'industry': 'technology',
            'loan_amount': 100000,
            'loan_purpose': 'expansion',
            'business_credit_score': 70,
            'collateral_value': 200000,
            'cash_flow': 80000
        }
    }
    
    for app_type, application in applications.items():
        logger.info(f"Running stress tests for {app_type} application...")
        
        stress_results = app.run_stress_tests(application, app_type)
        
        # Display baseline results
        baseline = stress_results['baseline_decision']
        logger.info(f"  Baseline Decision: {baseline['decision'].upper()}")
        logger.info(f"  Baseline Risk Score: {baseline.get('risk_score', 0):.3f}")
        
        # Display stress test results
        logger.info("  Stress Test Results:")
        for scenario_name, scenario_result in stress_results['scenario_results'].items():
            decision = scenario_result['decision']
            change_indicator = "📈" if scenario_result['decision_change'] else "📊"
            risk_change = scenario_result['risk_score_change']
            
            logger.info(f"    {change_indicator} {scenario_name}:")
            logger.info(f"      Decision: {decision['decision'].upper()}")
            logger.info(f"      Risk Score: {decision.get('risk_score', 0):.3f} ({risk_change:+.3f})")
        
        # Display summary
        summary = stress_results['summary']
        logger.info(f"  Summary:")
        logger.info(f"    Decision Changes: {summary['decision_changes']}/{len(stress_results['scenario_results'])}")
        logger.info(f"    Risk Range: {summary['best_case_risk_score']:.3f} - {summary['worst_case_risk_score']:.3f}")
        logger.info(f"    Stable Decision: {'Yes' if summary['stable_decision'] else 'No'}")
        logger.info("")


def demonstrate_configuration(logger):
    """Demonstrate configuration management."""
    logger.info("=== Configuration Management ===")
    
    # Get current configuration
    config = get_config()
    
    logger.info("Current configuration:")
    logger.info(f"  Min Credit Score: {config.get('credit_application', 'min_credit_score')}")
    logger.info(f"  Max DTI: {config.get('credit_application', 'max_dti')}")
    logger.info(f"  Risk Thresholds: {config.get('risk_assessment', 'risk_thresholds')}")
    
    # Demonstrate custom configuration
    custom_config = Config()
    custom_config.set('credit_application', 'min_credit_score', 650)
    custom_config.set('credit_application', 'max_dti', 0.4)
    
    logger.info("Custom configuration:")
    logger.info(f"  Min Credit Score: {custom_config.get('credit_application', 'min_credit_score')}")
    logger.info(f"  Max DTI: {custom_config.get('credit_application', 'max_dti')}")
    
    # Validate configuration
    try:
        custom_config.validate()
        logger.info("  Configuration is valid")
    except Exception as e:
        logger.error(f"  Configuration error: {e}")


def save_results_to_file(results: Dict[str, Any], filename: str, logger):
    """Save results to JSON file."""
    try:
        output_path = Path(filename)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving results: {e}")


def main():
    """Main example function."""
    logger = setup_example()
    
    try:
        # Initialize credit application with default configuration
        app = CreditApplication()
        
        # Set up realistic economic conditions
        economic_data = {
            'gdp_growth': 0.025,
            'unemployment_rate': 0.045,
            'inflation_rate': 0.02,
            'interest_rate': 0.035,
            'market_volatility': 0.15,
            'industry_growth': {
                'technology': 0.08,
                'healthcare': 0.05,
                'manufacturing': 0.03,
                'retail': 0.01,
                'hospitality': -0.02
            }
        }
        app.economic_indicators.update_indicators(economic_data)
        
        logger.info("Economic indicators updated with current market conditions")
        logger.info("")
        
        # Collect all results
        all_results = {}
        
        # Run demonstrations
        all_results['individual_assessments'] = demonstrate_individual_assessment(app, logger)
        all_results['corporate_assessments'] = demonstrate_corporate_assessment(app, logger)
        
        demonstrate_economic_scenarios(app, logger)
        demonstrate_stress_testing(app, logger)
        demonstrate_configuration(logger)
        
        # Save results
        save_results_to_file(all_results, 'credit_assessment_results.json', logger)
        
        # Display available stress scenarios
        logger.info("=== Available Stress Test Scenarios ===")
        scenarios = app.get_stress_scenarios()
        for scenario in scenarios:
            logger.info(f"  🔥 {scenario['name']} - {scenario['title']}")
            logger.info(f"     {scenario['description']}")
        
        logger.info("")
        logger.info("✅ Example completed successfully!")
        logger.info("Check 'credit_assessment_results.json' for detailed results")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


if __name__ == '__main__':
    main()