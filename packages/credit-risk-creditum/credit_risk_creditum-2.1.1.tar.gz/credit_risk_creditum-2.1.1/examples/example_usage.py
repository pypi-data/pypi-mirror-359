from credit_risk.core.application import CreditApplication

def main():
    # Initialize application processor
    credit_app = CreditApplication(min_credit_score=600, max_dti=0.43)

    # Update economic indicators
    economic_data = {
        'cpi': 0.02,
        'gdp_growth': 0.03,
        'unemployment_rate': 0.05,
        'interest_rate': 0.04,
        'inflation_rate': 0.02,
        'industry_growth': {
            'technology': 0.08,
            'manufacturing': 0.03,
            'retail': 0.02
        },
        'market_volatility': 0.15,
        'currency_stability': 0.85
    }
    credit_app.economic_indicators.update_indicators(economic_data)

    # Process individual application
    individual_application = {
        'credit_score': 720,
        'income': 60000,  # Annual income (frontend uses 'income')
        'monthly_debt': 1500,
        'loan_amount': 20000,
        'loan_purpose': 'home_improvement',
        'employment_history': 'stable',  # Frontend field
        'debt_to_income_ratio': 30.0  # Calculated from monthly_debt and income
    }

    individual_decision = credit_app.make_decision(individual_application, 'individual')

    # Process corporate application
    corporate_application = {
        'years_in_business': 5,
        'revenue': 1000000,  # Frontend uses 'revenue' not 'annual_revenue'
        'industry': 'technology',
        'loan_amount': 200000,
        'loan_purpose': 'expansion',
        'business_credit_score': 75,  # Frontend field
        'collateral_value': 500000,  # Frontend field
        'cash_flow': 150000  # Frontend field
    }

    corporate_decision = credit_app.make_decision(corporate_application, 'corporate')

    # Display results
    print_results(individual_application, individual_decision, 'Individual')
    print_results(corporate_application, corporate_decision, 'Corporate')
    print_economic_conditions(economic_data)

def print_results(application: dict, decision: dict, application_type: str):
    print(f"\n=== {application_type} Credit Application Results ===")
    print(f"Decision: {decision['decision']}")
    print(f"Risk Score: {decision['risk_score']:.2f}")
    print(f"Risk Category: {decision['risk_category']}")
    print(f"Maximum Loan Amount: ${decision['max_loan_amount']:,.2f}")
    print(f"Economic Impact Factor: {decision['economic_factor']:.2f}")

    if application_type == 'Individual':
        monthly_income = application['income'] / 12
        dti_ratio = application['monthly_debt'] / monthly_income
        print("\nDetailed Individual Metrics:")
        print(f"Annual Income: ${application['income']:,.2f}")
        print(f"Monthly Debt: ${application['monthly_debt']:,.2f}")
        print(f"Debt-to-Income Ratio: {dti_ratio:.2%}")
        print(f"Employment History: {application['employment_history']}")
    else:
        print("\nDetailed Corporate Metrics:")
        print(f"Years in Business: {application['years_in_business']}")
        print(f"Annual Revenue: ${application['revenue']:,.2f}")
        print(f"Industry: {application['industry']}")
        print("\nFinancial Details:")
        print(f"Business Credit Score: {application['business_credit_score']}")
        print(f"Collateral Value: ${application['collateral_value']:,.2f}")
        print(f"Cash Flow: ${application['cash_flow']:,.2f}")

def print_economic_conditions(economic_data: dict):
    print("\n=== Current Economic Conditions ===")
    print(f"CPI Growth: {economic_data['cpi']:.1%}")
    print(f"GDP Growth: {economic_data['gdp_growth']:.1%}")
    print(f"Unemployment Rate: {economic_data['unemployment_rate']:.1%}")
    print(f"Interest Rate: {economic_data['interest_rate']:.1%}")
    print(f"Inflation Rate: {economic_data['inflation_rate']:.1%}")
    print(f"Market Volatility Index: {economic_data['market_volatility']:.2f}")
    print(f"Currency Stability Index: {economic_data['currency_stability']:.2f}")

if __name__ == "__main__":
    main()