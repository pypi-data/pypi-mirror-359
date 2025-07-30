Configuration Guide
==================

The NMF Standalone system is highly configurable through the options dictionary. This guide explains all available parameters.

Core Parameters
--------------

Language Settings
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - ``LANGUAGE``
     - str
     - "TR"
     - Language for text processing ("TR" for Turkish, "EN" for English)
   * - ``LEMMATIZE``
     - bool
     - True
     - Enable lemmatization (primarily for English text)

Topic Configuration
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - ``DESIRED_TOPIC_COUNT``
     - int
     - 5
     - Number of topics to extract from the corpus
   * - ``N_TOPICS``
     - int
     - 15
     - Number of top words to display per topic

Algorithm Settings
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - ``nmf_type``
     - str
     - "nmf"
     - NMF algorithm ("nmf" for standard, "opnmf" for orthogonal projective)
   * - ``tokenizer_type``
     - str
     - "bpe"
     - Tokenization method for Turkish ("bpe" or "wordpiece")

Output Settings
--------------

Visualization Options
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - ``gen_cloud``
     - bool
     - True
     - Generate word cloud images for each topic
   * - ``gen_topic_distribution``
     - bool
     - True
     - Create document distribution plots across topics
   * - ``save_excel``
     - bool
     - True
     - Export topic-word matrices to Excel format

File Processing
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - ``separator``
     - str
     - ","
     - CSV file separator character
   * - ``word_pairs_out``
     - bool
     - False
     - Calculate and output word co-occurrence statistics

Advanced Configuration
---------------------

NMF Algorithm Parameters
~~~~~~~~~~~~~~~~~~~~~~~

For fine-tuning the NMF algorithm behavior:

.. code-block:: python

   # These are internal parameters, typically not changed
   advanced_options = {
       "norm_thresh": 0.005,        # Convergence threshold
       "zero_threshold": 0.0001,    # Minimum value threshold
       "max_iterations": 1000,      # Maximum NMF iterations
   }

Filtering Options
~~~~~~~~~~~~~~~~

For specific data filtering:

.. code-block:: python

   filtering_options = {
       "filter_app": True,              # Enable app-specific filtering
       "filter_app_name": "BiP",        # Specific app name to filter
   }

Example Configurations
---------------------

High-Quality Analysis
~~~~~~~~~~~~~~~~~~~

For detailed analysis with maximum output:

.. code-block:: python

   high_quality_options = {
       "LEMMATIZE": True,
       "N_TOPICS": 25,                  # More words per topic
       "DESIRED_TOPIC_COUNT": 10,       # More topics
       "tokenizer_type": "wordpiece",   # More sophisticated tokenization
       "nmf_type": "opnmf",            # Better topic separation
       "LANGUAGE": "TR",
       "gen_cloud": True,
       "save_excel": True,
       "gen_topic_distribution": True,
       "word_pairs_out": True,          # Include co-occurrence analysis
   }

Fast Processing
~~~~~~~~~~~~~~

For quick analysis with minimal output:

.. code-block:: python

   fast_options = {
       "LEMMATIZE": False,
       "N_TOPICS": 10,                  # Fewer words per topic
       "DESIRED_TOPIC_COUNT": 3,        # Fewer topics
       "tokenizer_type": "bpe",         # Faster tokenization
       "nmf_type": "nmf",              # Standard algorithm
       "LANGUAGE": "TR",
       "gen_cloud": False,              # Skip word clouds
       "save_excel": False,             # Skip Excel export
       "gen_topic_distribution": False, # Skip plots
   }

Large Dataset Processing
~~~~~~~~~~~~~~~~~~~~~~

For handling large datasets efficiently:

.. code-block:: python

   large_dataset_options = {
       "LEMMATIZE": True,
       "N_TOPICS": 15,
       "DESIRED_TOPIC_COUNT": 8,
       "tokenizer_type": "bpe",         # More memory efficient
       "nmf_type": "nmf",              # Faster convergence
       "LANGUAGE": "EN",
       "gen_cloud": True,
       "save_excel": True,
       "gen_topic_distribution": False, # Skip for performance
       "word_pairs_out": False,         # Skip co-occurrence
   }

Best Practices
-------------

1. **Start Small**: Begin with fewer topics (3-5) and increase based on results
2. **Language-Specific Settings**: Use appropriate tokenization for each language
3. **Quality vs Speed**: Use OPNMF for better topic separation, standard NMF for speed
4. **Output Selection**: Disable unused visualizations for faster processing
5. **Memory Management**: Use BPE tokenization for large Turkish datasets