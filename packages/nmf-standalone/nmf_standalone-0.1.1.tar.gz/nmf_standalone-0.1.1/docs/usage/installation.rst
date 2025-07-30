Installation
============

Requirements
-----------

- Python 3.8 or higher
- UV package manager (recommended) or pip

Quick Install
------------

Using UV (Recommended)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone <repository-url>
   cd nmf-standalone
   
   # Install dependencies with UV
   uv pip install -r requirements.txt

Using Pip
~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt

Dependencies
-----------

Core Dependencies
~~~~~~~~~~~~~~~~

- **numpy**: Numerical computing
- **scipy**: Scientific computing and sparse matrices
- **pandas**: Data manipulation and analysis
- **scikit-learn**: Machine learning utilities
- **nltk**: Natural language processing toolkit
- **tokenizers**: Fast tokenization library
- **sqlalchemy**: Database toolkit

Visualization Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

- **matplotlib**: Plotting library
- **wordcloud**: Word cloud generation
- **gensim**: Topic modeling library (for coherence scoring)

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~

- **jupyter**: For notebook examples
- **pytest**: For running tests

Verification
-----------

To verify your installation, run:

.. code-block:: bash

   python -c "import standalone_nmf; print('Installation successful!')"