Installation Guide
==================

This guide covers installation of Credit Risk Creditum across different environments.

📦 Quick Installation
--------------------

PyPI Installation
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install credit-risk-creditum

Upgrade to Latest Version
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install --upgrade credit-risk-creditum

Specific Version
~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install credit-risk-creditum==1.1.2

🐍 Requirements
---------------

Python Version
~~~~~~~~~~~~~~

- **Python 3.8+** (recommended: Python 3.9 or later)

Dependencies
~~~~~~~~~~~

Core dependencies (automatically installed):

- ``numpy>=1.21.0,<2.0.0``
- ``pandas>=1.3.0``
- ``scikit-learn>=1.0.0``
- ``requests>=2.25.0``
- ``typing-extensions>=4.0.0``

🌐 Environment-Specific Installation
------------------------------------

Google Colab
~~~~~~~~~~~~

.. code-block:: python

   # In a Colab notebook cell
   !pip install credit-risk-creditum==1.1.2
   
   # Verify installation
   import credit_risk
   print(f"Version: {credit_risk.__version__}")

.. note::
   If you encounter import errors in Colab, restart the runtime after installation.

Jupyter Notebooks
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install in current kernel
   pip install credit-risk-creditum
   
   # Or use conda
   conda install -c conda-forge credit-risk-creditum

.. code-block:: python

   # In a notebook cell (alternative)
   import sys
   !{sys.executable} -m pip install credit-risk-creditum

Virtual Environment
~~~~~~~~~~~~~~~~~~

Using venv:

.. code-block:: bash

   # Create virtual environment
   python -m venv credit_risk_env
   
   # Activate (Linux/Mac)
   source credit_risk_env/bin/activate
   
   # Activate (Windows)
   credit_risk_env\\Scripts\\activate
   
   # Install package
   pip install credit-risk-creditum

Using conda:

.. code-block:: bash

   # Create conda environment
   conda create -n credit_risk python=3.9
   
   # Activate environment
   conda activate credit_risk
   
   # Install package
   pip install credit-risk-creditum

Docker
~~~~~~

.. code-block:: dockerfile

   FROM python:3.9-slim
   
   # Install package
   RUN pip install credit-risk-creditum==1.1.2
   
   # Your application code
   COPY . /app
   WORKDIR /app

🔧 Development Installation
--------------------------

From Source
~~~~~~~~~~

.. code-block:: bash

   # Clone repository
   git clone https://github.com/credit-risk-creditum/creditum.git
   cd creditum/python_package
   
   # Install in development mode
   pip install -e .

With Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install with development dependencies
   pip install credit-risk-creditum[dev]
   
   # Or from source
   pip install -e ".[dev]"

Development dependencies include:

- ``pytest>=7.0.0``
- ``pytest-cov>=4.0.0``
- ``black>=23.0.0``
- ``flake8>=6.0.0``
- ``mypy>=1.0.0``
- ``pre-commit>=3.0.0``

🧪 Verify Installation
----------------------

Basic Verification
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Test basic import
   try:
       import credit_risk
       print(f"✅ Credit Risk Creditum v{credit_risk.__version__} installed successfully")
   except ImportError as e:
       print(f"❌ Installation failed: {e}")

Functionality Test
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from credit_risk import CreditApplication
   
   # Initialize application
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
       print("✅ Package functionality verified")
       print(f"Test decision: {decision['decision']}")
       print(f"Available features: {list(decision.keys())}")
   except Exception as e:
       print(f"❌ Functionality test failed: {e}")

CLI Verification
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test CLI installation
   credit-risk --version
   
   # Test CLI functionality
   credit-risk scenarios --output table

🐛 Troubleshooting
------------------

Common Issues
~~~~~~~~~~~~

**Import Error: No module named 'credit_risk'**

.. code-block:: bash

   # Check if package is installed
   pip list | grep credit-risk-creditum
   
   # Reinstall if missing
   pip install --force-reinstall credit-risk-creditum

**Version Mismatch**

.. code-block:: python

   # Check current version
   import credit_risk
   print(f"Current version: {credit_risk.__version__}")
   
   # Upgrade to latest
   import subprocess
   subprocess.run(["pip", "install", "--upgrade", "credit-risk-creditum"])

**NumPy Compatibility Issues**

.. code-block:: bash

   # Install compatible NumPy version
   pip install "numpy>=1.21.0,<2.0.0"

**Dependency Conflicts**

.. code-block:: bash

   # Create clean environment
   python -m venv clean_env
   source clean_env/bin/activate  # Linux/Mac
   # clean_env\\Scripts\\activate  # Windows
   
   pip install credit-risk-creditum

Google Colab Specific Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**KeyError in Colab**

.. code-block:: python

   # Force reinstall latest version
   !pip uninstall credit-risk-creditum -y
   !pip cache purge
   !pip install credit-risk-creditum==1.1.2
   
   # Restart runtime: Runtime → Restart Runtime

**Runtime Restart Required**

.. code-block:: python

   # After installation, restart runtime and verify
   import credit_risk
   assert credit_risk.__version__ == "1.1.2", f"Wrong version: {credit_risk.__version__}"
   print("✅ Correct version installed")

Memory Issues
~~~~~~~~~~~~

.. code-block:: python

   # For large datasets, monitor memory usage
   import psutil
   import os
   
   process = psutil.Process(os.getpid())
   memory_usage = process.memory_info().rss / 1024 / 1024  # MB
   print(f"Memory usage: {memory_usage:.2f} MB")

🔧 Advanced Configuration
------------------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set environment variables for configuration
   export CREDIT_RISK_LOG_LEVEL=INFO
   export CREDIT_RISK_CACHE_ENABLED=true
   export CREDIT_RISK_MAX_DTI=0.43

Python Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from credit_risk.config import get_config
   
   # Get configuration
   config = get_config()
   
   # Modify settings
   config.set('credit_application', 'min_credit_score', 650)
   config.set('logging', 'level', 'DEBUG')

🌟 Optional Dependencies
-----------------------

Documentation
~~~~~~~~~~~~

.. code-block:: bash

   # Install documentation dependencies
   pip install credit-risk-creditum[docs]

Testing
~~~~~~

.. code-block:: bash

   # Install testing dependencies
   pip install credit-risk-creditum[test]

All Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install all optional dependencies
   pip install credit-risk-creditum[dev,docs,test]

🔄 Updating
-----------

Check for Updates
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check current version
   pip show credit-risk-creditum
   
   # Check latest version on PyPI
   pip index versions credit-risk-creditum

Automated Updates
~~~~~~~~~~~~~~~~

.. code-block:: python

   import subprocess
   import sys
   
   def update_package():
       """Update to latest version"""
       try:
           subprocess.run([
               sys.executable, "-m", "pip", "install", 
               "--upgrade", "credit-risk-creditum"
           ], check=True)
           print("✅ Package updated successfully")
       except subprocess.CalledProcessError:
           print("❌ Update failed")
   
   # update_package()

📋 System Requirements
---------------------

Minimum Requirements
~~~~~~~~~~~~~~~~~~~

- **RAM**: 512 MB available memory
- **Disk**: 100 MB free space
- **CPU**: Any modern CPU (no specific requirements)

Recommended Requirements
~~~~~~~~~~~~~~~~~~~~~~~

- **RAM**: 2 GB+ for large datasets
- **Disk**: 1 GB free space for development
- **CPU**: Multi-core for better performance with large portfolios

🎯 Next Steps
------------

After successful installation:

1. Read the :doc:`quickstart` guide
2. Try the :doc:`examples/google_colab` examples
3. Explore the :doc:`api/core` reference

📞 Support
----------

If you encounter installation issues:

1. Check our `GitHub Issues <https://github.com/credit-risk-creditum/creditum/issues>`_
2. Create a new issue with:
   - Your Python version
   - Operating system
   - Complete error message
   - Installation command used