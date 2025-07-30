Configuration Guide
===================

Basic Configuration
-------------------

.. code-block:: python

    app = CreditApplication(
        min_credit_score=600,
        max_dti=0.43,
        risk_thresholds={
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
    )

Economic Indicators
-------------------

.. code-block:: python

    app.economic_indicators.update_indicators({
        'cpi': 0.02,
        'gdp_growth': 0.03,
        'unemployment_rate': 0.05,
        'interest_rate': 0.04,
        'inflation_rate': 0.02,
        'industry_growth': {
            'technology': 0.08,
            'manufacturing': 0.03
        }
    })

Custom Risk Models
------------------

.. code-block:: python

    class CustomRiskModel(BaseRiskAssessment):
        def __init__(self, economic_indicators):
            super().__init__(economic_indicators)
            self.custom_weights = {
                'payment_history': 0.35,
                'credit_utilization': 0.25
            }