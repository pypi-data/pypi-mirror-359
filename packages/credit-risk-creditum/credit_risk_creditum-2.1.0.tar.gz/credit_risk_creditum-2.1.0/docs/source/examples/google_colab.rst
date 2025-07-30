Google Colab Examples
====================

This guide provides comprehensive examples for using Credit Risk Creditum in Google Colab notebooks.

🚀 Getting Started in Colab
---------------------------

Installation
~~~~~~~~~~~~

.. code-block:: python

   # Install the latest version
   !pip install --upgrade credit-risk-creditum==1.1.2
   
   # Verify installation
   import credit_risk
   print(f"Version: {credit_risk.__version__}")

.. note::
   If you encounter KeyError issues, restart the runtime and reinstall:
   
   .. code-block:: python
   
      # Restart runtime, then:
      !pip uninstall credit-risk-creditum -y
      !pip install credit-risk-creditum==1.1.2

📊 Basic Credit Assessment
--------------------------

Individual Credit Risk
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from credit_risk import CreditApplication

   # Initialize the application
   app = CreditApplication()

   # Individual application data
   individual_application = {
       'credit_score': 720,
       'monthly_income': 5000,
       'monthly_debt': 1500,
       'loan_amount': 25000,
       'loan_purpose': 'home'
   }

   # Make decision
   decision = app.make_decision(individual_application, 'individual')
   
   # Display results
   print(f"Decision: {decision['decision']}")
   print(f"Risk Score: {decision['risk_score']:.3f}")
   print(f"Risk Category: {decision['risk_category']}")
   print(f"Max Loan Amount: ${decision['max_loan_amount']:,.0f}")
   print(f"Economic Factor: {decision['economic_factor']:.3f}")

Corporate Credit Risk
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Corporate application data
   corporate_application = {
       'years_in_business': 5,
       'annual_revenue': 500000,
       'industry': 'technology',
       'loan_amount': 100000,
       'loan_purpose': 'expansion'
   }

   # Make decision
   corp_decision = app.make_decision(corporate_application, 'corporate')
   
   print(f"Corporate Decision: {corp_decision['decision']}")
   print(f"Risk Score: {corp_decision['risk_score']:.3f}")
   print(f"Risk Category: {corp_decision['risk_category']}")
   print(f"Max Loan Amount: ${corp_decision['max_loan_amount']:,.0f}")

🔬 Stress Testing Examples
--------------------------

View Available Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # List all available stress scenarios
   scenarios = app.get_stress_scenarios()
   print("Available Stress Scenarios:")
   print("=" * 50)
   
   for scenario in scenarios:
       print(f"📊 {scenario['name']}")
       print(f"   Description: {scenario['description']}")
       print()

Apply Specific Stress Scenario
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Test with specific stress scenario
   normal_decision = app.make_decision(individual_application, 'individual')
   recession_decision = app.make_decision(
       individual_application, 
       'individual', 
       stress_scenario='recession'
   )

   print("📈 Scenario Comparison:")
   print("-" * 40)
   print(f"Normal Conditions:")
   print(f"  Risk Score: {normal_decision['risk_score']:.3f}")
   print(f"  Decision: {normal_decision['decision']}")
   print()
   print(f"Recession Scenario:")
   print(f"  Risk Score: {recession_decision['risk_score']:.3f}")
   print(f"  Decision: {recession_decision['decision']}")
   print(f"  Economic Factor: {recession_decision['economic_factor']:.3f}")

Comprehensive Stress Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Run all stress scenarios at once
   stress_results = app.run_stress_tests(individual_application, 'individual')

   print("🔬 Comprehensive Stress Test Results:")
   print("=" * 50)
   print(f"Baseline Decision: {stress_results['baseline_decision']['decision']}")
   print(f"Baseline Risk Score: {stress_results['baseline_decision']['risk_score']:.3f}")
   print()
   print(f"Scenarios Tested: {len(stress_results['scenario_results'])}")
   print(f"Decision Changes: {stress_results['summary']['decision_changes']}")
   print(f"Worst Case Risk: {stress_results['summary']['worst_case_risk_score']:.3f}")
   print(f"Best Case Risk: {stress_results['summary']['best_case_risk_score']:.3f}")
   print()

   print("Individual Scenario Results:")
   print("-" * 30)
   for scenario_name, result in stress_results['scenario_results'].items():
       decision = result['decision']
       change_icon = "🔴" if result['decision_change'] else "🟢"
       risk_change = result['risk_score_change']
       
       print(f"{change_icon} {scenario_name}")
       print(f"   Decision: {decision['decision']}")
       print(f"   Risk Score: {decision['risk_score']:.3f} ({risk_change:+.3f})")
       print()

Compare Multiple Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Compare specific scenarios side by side
   test_scenarios = ['recession', 'inflation_surge', 'market_crash', 'optimistic']

   print("📊 Scenario Comparison Table:")
   print("=" * 60)
   print(f"{'Scenario':<15} {'Risk Score':<12} {'Decision':<10} {'Change'}")
   print("-" * 60)

   # Baseline
   baseline = app.make_decision(individual_application, 'individual')
   print(f"{'Baseline':<15} {baseline['risk_score']:<12.3f} {baseline['decision']:<10} {'---'}")

   # Test each scenario
   for scenario in test_scenarios:
       try:
           decision = app.make_decision(
               individual_application, 
               'individual', 
               stress_scenario=scenario
           )
           change = decision['risk_score'] - baseline['risk_score']
           change_str = f"{change:+.3f}"
           print(f"{scenario:<15} {decision['risk_score']:<12.3f} {decision['decision']:<10} {change_str}")
       except Exception as e:
           print(f"{scenario:<15} {'ERROR':<12} {'ERROR':<10} {str(e)[:10]}")

📈 Economic Indicators
----------------------

Update Economic Data
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Update economic indicators
   economic_data = {
       'gdp_growth': 0.02,
       'unemployment_rate': 0.04,
       'inflation_rate': 0.025,
       'interest_rate': 0.035
   }

   app.economic_indicators.update_indicators(economic_data)
   
   print("Updated Economic Indicators:")
   for key, value in economic_data.items():
       print(f"  {key.replace('_', ' ').title()}: {value:.3f}")

   # Test impact on risk assessment
   updated_decision = app.make_decision(individual_application, 'individual')
   print(f"\\nRisk Score with Updated Economics: {updated_decision['risk_score']:.3f}")

🎯 Real-World Examples
----------------------

Example 1: First-Time Homebuyer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # First-time homebuyer profile
   first_time_buyer = {
       'credit_score': 680,
       'monthly_income': 4200,
       'monthly_debt': 800,
       'loan_amount': 180000,
       'loan_purpose': 'home'
   }

   print("🏠 First-Time Homebuyer Assessment:")
   print("=" * 40)
   
   decision = app.make_decision(first_time_buyer, 'individual')
   print(f"Application Status: {decision['decision'].upper()}")
   print(f"Risk Category: {decision['risk_category'].upper()}")
   print(f"Risk Score: {decision['risk_score']:.3f}")
   print(f"Recommended Loan Amount: ${decision['max_loan_amount']:,.0f}")
   
   # Check stress scenarios
   stress_results = app.run_stress_tests(first_time_buyer, 'individual')
   if stress_results['summary']['decision_changes'] > 0:
       print(f"⚠️  Warning: Decision changes in {stress_results['summary']['decision_changes']} stress scenarios")
   else:
       print("✅ Decision stable across all stress scenarios")

Example 2: Small Business Loan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Small business loan application
   small_business = {
       'years_in_business': 3,
       'annual_revenue': 150000,
       'industry': 'retail',
       'loan_amount': 50000,
       'loan_purpose': 'equipment'
   }

   print("🏪 Small Business Loan Assessment:")
   print("=" * 40)
   
   decision = app.make_decision(small_business, 'corporate')
   print(f"Application Status: {decision['decision'].upper()}")
   print(f"Risk Category: {decision['risk_category'].upper()}")
   print(f"Risk Score: {decision['risk_score']:.3f}")
   print(f"Approved Loan Amount: ${decision['max_loan_amount']:,.0f}")

🛠️ Troubleshooting
------------------

Common Issues
~~~~~~~~~~~~~

**KeyError: 'risk_category'**

.. code-block:: python

   # Solution: Ensure you're using version 1.1.2+
   import credit_risk
   print(f"Current version: {credit_risk.__version__}")
   
   # If not 1.1.2, restart runtime and reinstall
   if credit_risk.__version__ != "1.1.2":
       print("⚠️  Please restart runtime and install version 1.1.2")

**Import Errors**

.. code-block:: python

   # Clear cache and reinstall
   !pip cache purge
   !pip uninstall credit-risk-creditum -y
   !pip install credit-risk-creditum==1.1.2
   
   # Restart runtime after installation

**NumPy Compatibility Issues**

.. code-block:: python

   # If you see NumPy compatibility warnings
   !pip install "numpy>=1.21.0,<2.0.0"
   
   # Restart runtime

Debug Information
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get debug information
   from credit_risk import CreditApplication
   
   app = CreditApplication()
   
   # Test basic functionality
   test_data = {
       'credit_score': 700,
       'monthly_income': 5000,
       'monthly_debt': 1000,
       'loan_amount': 20000,
       'loan_purpose': 'personal'
   }
   
   try:
       decision = app.make_decision(test_data, 'individual')
       print("✅ Package working correctly")
       print(f"Available keys: {list(decision.keys())}")
   except Exception as e:
       print(f"❌ Error: {e}")
       print("Please check installation and restart runtime")

📱 Mobile-Friendly Colab Tips
-----------------------------

For better mobile experience in Colab:

.. code-block:: python

   # Use shorter variable names
   app = CreditApplication()
   
   # Format output for mobile screens
   def print_decision(decision, title="Decision"):
       print(f"\\n{title}")
       print("=" * len(title))
       for key, value in decision.items():
           if isinstance(value, float):
               print(f"{key}: {value:.3f}")
           else:
               print(f"{key}: {value}")

   # Use this function for cleaner output
   decision = app.make_decision(individual_application, 'individual')
   print_decision(decision, "Credit Decision")

.. note::
   For more examples and interactive notebooks, visit our `GitHub repository <https://github.com/credit-risk-creditum/creditum/tree/main/examples>`_.