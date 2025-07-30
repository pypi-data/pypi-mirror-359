Stress Testing Guide
====================

This comprehensive guide covers all aspects of stress testing with Credit Risk Creditum.

🔬 Overview
-----------

Stress testing evaluates how credit decisions perform under adverse economic conditions. Our package provides built-in scenarios and the ability to create custom stress tests.

📊 Available Stress Scenarios
-----------------------------

List All Scenarios
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from credit_risk import CreditApplication
   
   app = CreditApplication()
   scenarios = app.get_stress_scenarios()
   
   print("Available Stress Scenarios:")
   print("=" * 50)
   for scenario in scenarios:
       print(f"🎯 {scenario['name']}")
       print(f"   📝 {scenario['description']}")
       if 'parameters' in scenario:
           print(f"   ⚙️  Parameters: {scenario['parameters']}")
       print()

Default Scenarios
~~~~~~~~~~~~~~~~

The package includes these built-in scenarios:

1. **Recession**
   - High unemployment (8-12%)
   - Negative GDP growth (-2% to -5%)
   - Higher default rates

2. **Inflation Surge**
   - High inflation (6-10%)
   - Rising interest rates
   - Reduced purchasing power

3. **Market Crash**
   - Extreme market volatility
   - Credit market freeze
   - Increased risk premiums

4. **Optimistic**
   - Strong economic growth
   - Low unemployment
   - Favorable credit conditions

🎯 Single Scenario Testing
--------------------------

Basic Scenario Application
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Your application data
   application_data = {
       'credit_score': 720,
       'monthly_income': 5000,
       'monthly_debt': 1500,
       'loan_amount': 25000,
       'loan_purpose': 'home'
   }

   # Normal conditions
   normal_decision = app.make_decision(application_data, 'individual')
   
   # Apply recession scenario
   recession_decision = app.make_decision(
       application_data, 
       'individual', 
       stress_scenario='recession'
   )

   print("Normal vs Recession Comparison:")
   print("=" * 40)
   print(f"Normal Decision: {normal_decision['decision']}")
   print(f"Normal Risk Score: {normal_decision['risk_score']:.3f}")
   print()
   print(f"Recession Decision: {recession_decision['decision']}")
   print(f"Recession Risk Score: {recession_decision['risk_score']:.3f}")
   print(f"Risk Increase: {recession_decision['risk_score'] - normal_decision['risk_score']:+.3f}")

Scenario Impact Analysis
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_scenario_impact(app, application_data, scenario_name, entity_type='individual'):
       """Analyze the impact of a specific scenario"""
       
       # Get baseline
       baseline = app.make_decision(application_data, entity_type)
       
       # Apply scenario
       scenario_result = app.make_decision(
           application_data, 
           entity_type, 
           stress_scenario=scenario_name
       )
       
       # Calculate impacts
       risk_change = scenario_result['risk_score'] - baseline['risk_score']
       decision_change = scenario_result['decision'] != baseline['decision']
       loan_change = scenario_result['max_loan_amount'] - baseline['max_loan_amount']
       
       return {
           'scenario': scenario_name,
           'baseline_risk': baseline['risk_score'],
           'scenario_risk': scenario_result['risk_score'],
           'risk_change': risk_change,
           'decision_change': decision_change,
           'baseline_decision': baseline['decision'],
           'scenario_decision': scenario_result['decision'],
           'loan_amount_change': loan_change
       }

   # Test multiple scenarios
   scenarios_to_test = ['recession', 'inflation_surge', 'market_crash']
   
   print("📊 Scenario Impact Analysis:")
   print("=" * 60)
   print(f"{'Scenario':<15} {'Risk Δ':<10} {'Decision':<15} {'Loan Δ'}")
   print("-" * 60)
   
   for scenario in scenarios_to_test:
       impact = analyze_scenario_impact(app, application_data, scenario)
       
       decision_status = "CHANGED" if impact['decision_change'] else "SAME"
       risk_change_str = f"{impact['risk_change']:+.3f}"
       loan_change_str = f"${impact['loan_amount_change']:+,.0f}"
       
       print(f"{scenario:<15} {risk_change_str:<10} {decision_status:<15} {loan_change_str}")

📈 Comprehensive Stress Testing
-------------------------------

Full Stress Test Suite
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Run comprehensive stress tests
   stress_results = app.run_stress_tests(application_data, 'individual')

   print("🔬 Comprehensive Stress Test Results:")
   print("=" * 50)
   
   # Summary statistics
   summary = stress_results['summary']
   print(f"Baseline Decision: {stress_results['baseline_decision']['decision']}")
   print(f"Baseline Risk Score: {stress_results['baseline_decision']['risk_score']:.3f}")
   print()
   print(f"📊 Summary Statistics:")
   print(f"   Scenarios Tested: {len(stress_results['scenario_results'])}")
   print(f"   Decision Changes: {summary['decision_changes']}")
   print(f"   Worst Case Risk: {summary['worst_case_risk_score']:.3f}")
   print(f"   Best Case Risk: {summary['best_case_risk_score']:.3f}")
   print(f"   Decision Stability: {'✅ Stable' if summary['stable_decision'] else '⚠️ Unstable'}")

Detailed Results Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analyze each scenario in detail
   print("\\n📋 Detailed Scenario Results:")
   print("=" * 70)
   print(f"{'Scenario':<15} {'Decision':<10} {'Risk':<8} {'Change':<8} {'Status'}")
   print("-" * 70)
   
   baseline_risk = stress_results['baseline_decision']['risk_score']
   
   for scenario_name, result in stress_results['scenario_results'].items():
       decision = result['decision']
       risk_score = decision['risk_score']
       risk_change = risk_score - baseline_risk
       decision_change = result['decision_change']
       
       # Status indicators
       if decision_change:
           status = "🔴 RISK"
       elif risk_change > 0.1:
           status = "🟡 WATCH"
       else:
           status = "🟢 OK"
       
       print(f"{scenario_name:<15} {decision['decision']:<10} {risk_score:<8.3f} {risk_change:+8.3f} {status}")

Risk Distribution Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analyze risk score distribution across scenarios
   risk_scores = []
   scenario_names = []
   
   # Add baseline
   risk_scores.append(stress_results['baseline_decision']['risk_score'])
   scenario_names.append('baseline')
   
   # Add scenario results
   for scenario_name, result in stress_results['scenario_results'].items():
       risk_scores.append(result['decision']['risk_score'])
       scenario_names.append(scenario_name)
   
   # Calculate statistics
   import statistics
   
   mean_risk = statistics.mean(risk_scores)
   median_risk = statistics.median(risk_scores)
   std_risk = statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0
   
   print("\\n📊 Risk Score Distribution:")
   print("=" * 40)
   print(f"Mean Risk Score: {mean_risk:.3f}")
   print(f"Median Risk Score: {median_risk:.3f}")
   print(f"Standard Deviation: {std_risk:.3f}")
   print(f"Range: {min(risk_scores):.3f} - {max(risk_scores):.3f}")

🏢 Corporate Stress Testing
---------------------------

Corporate-Specific Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Corporate application
   corporate_app = {
       'years_in_business': 5,
       'annual_revenue': 500000,
       'industry': 'technology',
       'loan_amount': 100000,
       'loan_purpose': 'expansion'
   }

   # Corporate stress testing
   corp_stress_results = app.run_stress_tests(corporate_app, 'corporate')

   print("🏢 Corporate Stress Test Results:")
   print("=" * 50)
   
   baseline = corp_stress_results['baseline_decision']
   print(f"Baseline: {baseline['decision']} (Risk: {baseline['risk_score']:.3f})")
   print(f"Max Loan: ${baseline['max_loan_amount']:,.0f}")
   print()
   
   # Industry-specific impacts
   print("Industry Impact Analysis:")
   for scenario_name, result in corp_stress_results['scenario_results'].items():
       decision = result['decision']
       economic_factor = decision.get('economic_factor', 0)
       
       print(f"   {scenario_name}: Economic Factor = {economic_factor:.3f}")

🎯 Custom Stress Testing
------------------------

Portfolio Stress Testing
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Test multiple applications
   portfolio = [
       {
           'data': {'credit_score': 720, 'monthly_income': 5000, 'monthly_debt': 1500, 'loan_amount': 25000, 'loan_purpose': 'home'},
           'type': 'individual',
           'id': 'APP001'
       },
       {
           'data': {'credit_score': 680, 'monthly_income': 4200, 'monthly_debt': 800, 'loan_amount': 180000, 'loan_purpose': 'home'},
           'type': 'individual', 
           'id': 'APP002'
       },
       {
           'data': {'years_in_business': 3, 'annual_revenue': 150000, 'industry': 'retail', 'loan_amount': 50000, 'loan_purpose': 'equipment'},
           'type': 'corporate',
           'id': 'APP003'
       }
   ]

   def stress_test_portfolio(portfolio, scenario='recession'):
       """Stress test entire portfolio"""
       results = []
       
       for application in portfolio:
           baseline = app.make_decision(application['data'], application['type'])
           stressed = app.make_decision(application['data'], application['type'], stress_scenario=scenario)
           
           results.append({
               'id': application['id'],
               'type': application['type'],
               'baseline_decision': baseline['decision'],
               'stressed_decision': stressed['decision'],
               'risk_change': stressed['risk_score'] - baseline['risk_score'],
               'decision_change': baseline['decision'] != stressed['decision']
           })
       
       return results

   # Test portfolio under recession
   portfolio_results = stress_test_portfolio(portfolio, 'recession')

   print("🏦 Portfolio Stress Test (Recession):")
   print("=" * 50)
   print(f"{'ID':<8} {'Type':<12} {'Baseline':<10} {'Stressed':<10} {'Risk Δ'}")
   print("-" * 50)
   
   decision_changes = 0
   for result in portfolio_results:
       if result['decision_change']:
           decision_changes += 1
           
       print(f"{result['id']:<8} {result['type']:<12} {result['baseline_decision']:<10} {result['stressed_decision']:<10} {result['risk_change']:+.3f}")
   
   print(f"\\nPortfolio Impact: {decision_changes}/{len(portfolio)} applications changed decisions")

Scenario Sensitivity Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def sensitivity_analysis(app, application_data, entity_type='individual'):
       """Analyze sensitivity across all scenarios"""
       
       scenarios = ['recession', 'inflation_surge', 'market_crash', 'optimistic']
       baseline = app.make_decision(application_data, entity_type)
       
       sensitivity_results = {
           'baseline_risk': baseline['risk_score'],
           'scenario_impacts': {},
           'most_sensitive_scenario': None,
           'max_risk_increase': 0
       }
       
       for scenario in scenarios:
           try:
               result = app.make_decision(application_data, entity_type, stress_scenario=scenario)
               risk_change = result['risk_score'] - baseline['risk_score']
               
               sensitivity_results['scenario_impacts'][scenario] = {
                   'risk_score': result['risk_score'],
                   'risk_change': risk_change,
                   'decision': result['decision'],
                   'decision_change': result['decision'] != baseline['decision']
               }
               
               # Track most sensitive scenario
               if risk_change > sensitivity_results['max_risk_increase']:
                   sensitivity_results['max_risk_increase'] = risk_change
                   sensitivity_results['most_sensitive_scenario'] = scenario
                   
           except Exception as e:
               print(f"Error testing {scenario}: {e}")
       
       return sensitivity_results

   # Run sensitivity analysis
   sensitivity = sensitivity_analysis(app, application_data)

   print("🎯 Sensitivity Analysis:")
   print("=" * 40)
   print(f"Baseline Risk Score: {sensitivity['baseline_risk']:.3f}")
   print(f"Most Sensitive to: {sensitivity['most_sensitive_scenario']}")
   print(f"Maximum Risk Increase: +{sensitivity['max_risk_increase']:.3f}")
   print()
   
   print("Scenario Sensitivity Ranking:")
   sorted_scenarios = sorted(
       sensitivity['scenario_impacts'].items(),
       key=lambda x: x[1]['risk_change'],
       reverse=True
   )
   
   for i, (scenario, impact) in enumerate(sorted_scenarios, 1):
       change_icon = "📈" if impact['risk_change'] > 0 else "📉"
       print(f"{i}. {change_icon} {scenario}: {impact['risk_change']:+.3f}")

⚡ Performance Tips
------------------

Batch Processing
~~~~~~~~~~~~~~~

.. code-block:: python

   # For large portfolios, process in batches
   def batch_stress_test(applications, batch_size=100):
       """Process stress tests in batches for better performance"""
       
       total_apps = len(applications)
       results = []
       
       for i in range(0, total_apps, batch_size):
           batch = applications[i:i + batch_size]
           print(f"Processing batch {i//batch_size + 1}/{(total_apps-1)//batch_size + 1}")
           
           for app_data in batch:
               try:
                   stress_result = app.run_stress_tests(app_data['data'], app_data['type'])
                   results.append({
                       'id': app_data['id'],
                       'results': stress_result
                   })
               except Exception as e:
                   print(f"Error processing {app_data['id']}: {e}")
       
       return results

Caching Results
~~~~~~~~~~~~~~

.. code-block:: python

   # Cache stress test results for repeated analysis
   stress_cache = {}

   def cached_stress_test(app_data, entity_type, cache_key=None):
       """Cache stress test results to avoid recomputation"""
       
       if cache_key is None:
           cache_key = f"{entity_type}_{hash(str(app_data))}"
       
       if cache_key in stress_cache:
           print(f"Using cached results for {cache_key}")
           return stress_cache[cache_key]
       
       print(f"Computing stress test for {cache_key}")
       results = app.run_stress_tests(app_data, entity_type)
       stress_cache[cache_key] = results
       
       return results

   # Example usage
   cached_results = cached_stress_test(application_data, 'individual', 'test_app_1')

🎯 Best Practices
----------------

1. **Always test baseline first** - Understand normal conditions before stress testing
2. **Test multiple scenarios** - Don't rely on a single stress scenario
3. **Document assumptions** - Keep track of economic assumptions in each scenario
4. **Monitor decision stability** - Flag applications with high sensitivity
5. **Regular updates** - Update economic indicators regularly for accurate stress testing
6. **Portfolio analysis** - Test entire portfolios, not just individual applications
7. **Validate results** - Cross-check stress test results with historical data when available

📚 Further Reading
-----------------

- `API Reference <../api/core.html>`_ - Detailed API documentation
- `Economic Indicators Guide <../user_guide/economic_indicators.html>`_ - Understanding economic factors
- `Configuration <../user_guide/configuration.html>`_ - Customizing stress test parameters