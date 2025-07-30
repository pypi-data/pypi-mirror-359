Quick Start Guide
=================

Get up and running with Credit Risk Creditum in minutes.

🚀 5-Minute Setup
-----------------

1. Install the Package
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install credit-risk-creditum

2. Import and Initialize
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from credit_risk import CreditApplication
   
   # Create application processor
   app = CreditApplication()

3. Make Your First Assessment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Individual credit application
   application = {
       'credit_score': 720,
       'monthly_income': 5000,
       'monthly_debt': 1500,
       'loan_amount': 25000,
       'loan_purpose': 'home'
   }
   
   # Get decision
   decision = app.make_decision(application, 'individual')
   
   print(f"Decision: {decision['decision']}")
   print(f"Risk Score: {decision['risk_score']:.3f}")
   print(f"Risk Category: {decision['risk_category']}")

📊 Complete First Example
-------------------------

.. code-block:: python

   from credit_risk import CreditApplication
   
   # Initialize
   app = CreditApplication()
   
   # Update economic conditions (optional)
   economic_data = {
       'gdp_growth': 0.025,
       'unemployment_rate': 0.045,
       'inflation_rate': 0.02,
       'interest_rate': 0.035
   }
   app.economic_indicators.update_indicators(economic_data)
   
   # Individual assessment
   individual_app = {
       'credit_score': 720,
       'monthly_income': 5000,
       'monthly_debt': 1500,
       'loan_amount': 25000,
       'loan_purpose': 'home_improvement'
   }
   
   decision = app.make_decision(individual_app, 'individual')
   
   print("=== Credit Decision ===")
   print(f"Status: {decision['decision'].upper()}")
   print(f"Risk Score: {decision['risk_score']:.3f}")
   print(f"Risk Category: {decision['risk_category'].upper()}")
   print(f"Max Loan Amount: ${decision['max_loan_amount']:,.0f}")
   print(f"Economic Factor: {decision['economic_factor']:.3f}")

🏢 Corporate Assessment
-----------------------

.. code-block:: python

   # Corporate credit application
   corporate_app = {
       'years_in_business': 5,
       'annual_revenue': 500000,
       'industry': 'technology',
       'loan_amount': 100000,
       'loan_purpose': 'expansion'
   }
   
   corp_decision = app.make_decision(corporate_app, 'corporate')
   
   print("=== Corporate Credit Decision ===")
   print(f"Status: {corp_decision['decision'].upper()}")
   print(f"Risk Score: {corp_decision['risk_score']:.3f}")
   print(f"Max Loan Amount: ${corp_decision['max_loan_amount']:,.0f}")

🔬 Stress Testing
-----------------

.. code-block:: python

   # View available scenarios
   scenarios = app.get_stress_scenarios()
   print("Available Stress Scenarios:")
   for scenario in scenarios[:3]:  # Show first 3
       print(f"- {scenario['name']}: {scenario['description']}")
   
   # Test specific scenario
   recession_decision = app.make_decision(
       individual_app, 
       'individual', 
       stress_scenario='recession'
   )
   
   print(f"\\nRecession Scenario:")
   print(f"Risk Score: {recession_decision['risk_score']:.3f}")
   print(f"Decision: {recession_decision['decision']}")
   
   # Comprehensive stress testing
   stress_results = app.run_stress_tests(individual_app, 'individual')
   print(f"\\nStress Test Summary:")
   print(f"Scenarios tested: {len(stress_results['scenario_results'])}")
   print(f"Decision changes: {stress_results['summary']['decision_changes']}")

💻 Command Line Interface
-------------------------

.. code-block:: bash

   # Check version
   credit-risk --version
   
   # Assess credit application
   credit-risk assess --type individual --data '{
       "credit_score": 720,
       "monthly_income": 5000,
       "monthly_debt": 1500,
       "loan_amount": 25000,
       "loan_purpose": "home"
   }'
   
   # Run stress tests
   credit-risk stress-test --type individual --data '{
       "credit_score": 720,
       "monthly_income": 5000,
       "monthly_debt": 1500,
       "loan_amount": 25000,
       "loan_purpose": "home"
   }'
   
   # List available scenarios
   credit-risk scenarios

📱 Google Colab Quick Start
---------------------------

.. code-block:: python

   # Install in Colab
   !pip install credit-risk-creditum==1.1.2
   
   # Import and test
   from credit_risk import CreditApplication
   
   app = CreditApplication()
   
   # Quick test
   test_app = {
       'credit_score': 720,
       'monthly_income': 5000,
       'monthly_debt': 1500,
       'loan_amount': 25000,
       'loan_purpose': 'home'
   }
   
   decision = app.make_decision(test_app, 'individual')
   print("✅ Package working in Colab!")
   print(f"Decision: {decision['decision']}")

🎯 Common Use Cases
------------------

High-Risk Application
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   high_risk_app = {
       'credit_score': 580,
       'monthly_income': 3000,
       'monthly_debt': 2500,
       'loan_amount': 15000,
       'loan_purpose': 'debt_consolidation'
   }
   
   decision = app.make_decision(high_risk_app, 'individual')
   print(f"High-risk result: {decision['decision']} (Risk: {decision['risk_score']:.3f})")

Startup Company
~~~~~~~~~~~~~~

.. code-block:: python

   startup_app = {
       'years_in_business': 1,
       'annual_revenue': 50000,
       'industry': 'technology',
       'loan_amount': 25000,
       'loan_purpose': 'working_capital'
   }
   
   decision = app.make_decision(startup_app, 'corporate')
   print(f"Startup result: {decision['decision']} (Risk: {decision['risk_score']:.3f})")

Portfolio Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Multiple applications
   applications = [
       ({'credit_score': 720, 'monthly_income': 5000, 'monthly_debt': 1500, 'loan_amount': 25000, 'loan_purpose': 'home'}, 'individual'),
       ({'credit_score': 680, 'monthly_income': 4200, 'monthly_debt': 800, 'loan_amount': 180000, 'loan_purpose': 'home'}, 'individual'),
       ({'years_in_business': 5, 'annual_revenue': 500000, 'industry': 'tech', 'loan_amount': 100000, 'loan_purpose': 'expansion'}, 'corporate')
   ]
   
   print("Portfolio Analysis:")
   for i, (app_data, app_type) in enumerate(applications, 1):
       decision = app.make_decision(app_data, app_type)
       print(f"App {i}: {decision['decision']} (Risk: {decision['risk_score']:.3f})")

🔧 Configuration
----------------

Basic Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from credit_risk.config import get_config
   
   # Get current configuration
   config = get_config()
   
   # Modify settings
   config.set('credit_application', 'min_credit_score', 650)
   config.set('credit_application', 'max_dti', 0.40)
   
   # Create new application with updated settings
   app = CreditApplication(min_credit_score=650, max_dti=0.40)

Logging Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from credit_risk.logging_config import setup_logging, get_logger
   
   # Enable logging
   setup_logging(log_level='INFO')
   logger = get_logger('my_analysis')
   
   # Your analysis code
   logger.info("Starting credit risk analysis")
   decision = app.make_decision(application, 'individual')
   logger.info(f"Decision made: {decision['decision']}")

🚨 Troubleshooting Quick Fixes
------------------------------

KeyError Issues
~~~~~~~~~~~~~~

.. code-block:: python

   # Check version
   import credit_risk
   print(f"Version: {credit_risk.__version__}")
   
   # Should be 1.1.2 or later
   if credit_risk.__version__ < "1.1.2":
       print("Please upgrade: pip install --upgrade credit-risk-creditum")

Import Errors
~~~~~~~~~~~~

.. code-block:: python

   # Test imports one by one
   try:
       from credit_risk import CreditApplication
       print("✅ Main import successful")
   except ImportError as e:
       print(f"❌ Import failed: {e}")
       
   try:
       app = CreditApplication()
       print("✅ Initialization successful")
   except Exception as e:
       print(f"❌ Initialization failed: {e}")

Verification Script
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def verify_installation():
       """Complete verification script"""
       try:
           # Test import
           from credit_risk import CreditApplication
           print("✅ Import successful")
           
           # Test initialization
           app = CreditApplication()
           print("✅ Initialization successful")
           
           # Test basic functionality
           test_data = {
               'credit_score': 700,
               'monthly_income': 5000,
               'monthly_debt': 1000,
               'loan_amount': 20000,
               'loan_purpose': 'personal'
           }
           
           decision = app.make_decision(test_data, 'individual')
           
           # Check all required fields
           required_fields = ['decision', 'risk_score', 'risk_category', 'max_loan_amount']
           for field in required_fields:
               if field not in decision:
                   raise KeyError(f"Missing field: {field}")
           
           print("✅ All functionality verified")
           print(f"Version: {credit_risk.__version__}")
           return True
           
       except Exception as e:
           print(f"❌ Verification failed: {e}")
           return False
   
   # Run verification
   verify_installation()

📚 Next Steps
------------

After completing this quick start:

1. **Explore Examples**: Check out :doc:`examples/google_colab` for detailed examples
2. **Learn Stress Testing**: Read the :doc:`examples/stress_testing_guide` 
3. **API Reference**: Browse the :doc:`api/core` documentation
4. **Advanced Features**: Explore :doc:`user_guide/stress_testing` for advanced scenarios

🔗 Useful Links
---------------

- **PyPI Package**: https://pypi.org/project/credit-risk-creditum/
- **GitHub Repository**: https://github.com/credit-risk-creditum/creditum
- **Issue Tracker**: https://github.com/credit-risk-creditum/creditum/issues
- **Examples**: https://github.com/credit-risk-creditum/creditum/tree/main/examples