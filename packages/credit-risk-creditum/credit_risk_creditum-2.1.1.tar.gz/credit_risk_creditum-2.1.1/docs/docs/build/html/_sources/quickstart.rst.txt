Quick Start Guide
=================

This guide will help you get started with the Credit Risk Assessment package quickly.

Basic Setup
-----------

1. Installation:

.. code-block:: bash

    pip install credit-risk-assessment

2. Import required modules:

.. code-block:: python

    from credit_risk.core import CreditApplication
    from credit_risk.models import IndividualRiskAssessment

First Assessment
----------------

Create your first credit risk assessment:

.. code-block:: python

    # Initialize
    app = CreditApplication()

    # Create application data
    application = {
        'credit_score': 720,
        'monthly_income': 5000,
        'monthly_debt': 1500,
        'loan_amount': 20000,
        'loan_purpose': 'home_improvement'
    }

    # Get decision
    result = app.make_decision(application, 'individual')

Next Steps
----------

- Configure economic indicators
- Customize risk thresholds
- Implement custom models
- Set up monitoring