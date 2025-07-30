Machine Learning Models
=======================

The package includes sophisticated machine learning models for credit risk assessment.

Model Types
-----------

Random Forest Classifier
^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from credit_risk.models import BaseRiskAssessment
    
    model = app.individual_assessment.train_model(X, y, model_type='random_forest')
    
Features used:
- Payment history
- Credit utilization
- Income stability
- Debt-to-income ratio

Hyperparameters:
- n_estimators: 100
- max_depth: 10
- random_state: 42

Logistic Regression
^^^^^^^^^^^^^^^^^^^
Used for interpretable predictions with linear decision boundaries.

.. code-block:: python

    model = app.individual_assessment.train_model(X, y, model_type='logistic_regression')

Model Performance Metrics
-------------------------

.. code-block:: python

    # Get model performance
    performance = model.get_performance_metrics()
    print(f"Accuracy: {performance['accuracy']}")
    print(f"Precision: {performance['precision']}")
    print(f"Recall: {performance['recall']}")