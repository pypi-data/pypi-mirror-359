Installation
============

This section provides instructions on how to install the Credit Risk Assessment package.

Prerequisites
-------------
Ensure you have the following dependencies installed:

- Python 3.8 or higher
- pip
- Virtual environment (optional but recommended)

Installation Steps
------------------
1. Clone the repository:
   
   .. code-block:: bash

      git clone https://github.com/omoshola-o/credit-risk-creditum.git
      cd credit-risk-creditum

2. (Optional) Create and activate a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install the required dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

4. Verify the installation:

   .. code-block:: bash

      python -c "import credit_risk; print(credit_risk.__version__)"
