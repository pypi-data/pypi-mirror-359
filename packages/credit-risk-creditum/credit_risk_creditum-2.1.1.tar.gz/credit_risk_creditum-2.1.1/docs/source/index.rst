Credit Risk Creditum Documentation
===================================

.. image:: https://badge.fury.io/py/credit-risk-creditum.svg
   :target: https://badge.fury.io/py/credit-risk-creditum
   :alt: PyPI version

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

**Credit Risk Creditum** is a comprehensive Python package for credit risk assessment and stress testing with real-time economic data integration. Built for financial institutions, fintech companies, and researchers who need robust, explainable credit risk evaluation.

🌟 Features
-----------

- **Advanced Credit Scoring**: Individual and corporate credit risk assessment
- **Economic Integration**: Real-time economic indicators and stress testing  
- **Stress Testing**: Multi-scenario analysis for portfolio resilience
- **Machine Learning Ready**: Built-in support for scikit-learn models
- **Easy Integration**: Simple API for seamless integration
- **Comprehensive Documentation**: Detailed guides and examples

🚀 Quick Start
--------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install credit-risk-creditum

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from credit_risk import CreditApplication

   # Initialize the credit application processor
   app = CreditApplication()

   # Assess individual credit risk
   individual_application = {
       'credit_score': 720,
       'monthly_income': 5000,
       'monthly_debt': 1500,
       'loan_amount': 25000,
       'loan_purpose': 'home_improvement'
   }

   decision = app.make_decision(individual_application, 'individual')
   print(f"Decision: {decision['decision']}")
   print(f"Risk Score: {decision['risk_score']:.3f}")
   print(f"Risk Category: {decision['risk_category']}")

📚 Documentation Contents
-------------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   basic_usage

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/individual_assessment
   user_guide/corporate_assessment
   user_guide/stress_testing
   user_guide/economic_indicators
   user_guide/configuration

.. toctree::
   :maxdepth: 2
   :caption: Examples & Tutorials

   examples/google_colab
   examples/stress_testing_guide
   examples/scenario_comparison
   examples/jupyter_notebooks
   examples/real_world_examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/models
   api/utils
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   advanced/customization
   advanced/ml_integration
   advanced/performance
   advanced/security
   advanced/regulatory_compliance

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide

   contributing
   development
   testing
   changelog

🎯 Use Cases
------------

- **Banks & Credit Unions**: Enhance underwriting with stress testing
- **Fintech Platforms**: Integrate advanced risk assessment
- **Portfolio Management**: Analyze credit portfolio resilience
- **Regulatory Compliance**: Meet stress testing requirements
- **Academic Research**: Study credit risk dynamics

🔗 Links
--------

- **PyPI Package**: https://pypi.org/project/credit-risk-creditum/
- **GitHub Repository**: https://github.com/credit-risk-creditum/creditum
- **Bug Reports**: https://github.com/credit-risk-creditum/creditum/issues
- **Feature Requests**: https://github.com/credit-risk-creditum/creditum/issues/new

📄 License
----------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/credit-risk-creditum/creditum/blob/main/LICENSE>`_ file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
