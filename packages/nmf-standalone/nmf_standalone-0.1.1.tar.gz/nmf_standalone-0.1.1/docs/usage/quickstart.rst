Quick Start Guide
=================

This guide will help you get started with NMF Standalone for topic modeling.

Basic Usage
-----------

Turkish Text Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from standalone_nmf import run_standalone_nmf
   
   # Configuration for Turkish text
   options = {
       "LEMMATIZE": False,              # Not needed for Turkish
       "N_TOPICS": 15,                  # Words per topic
       "DESIRED_TOPIC_COUNT": 5,        # Number of topics
       "tokenizer_type": "bpe",         # Tokenization method
       "nmf_type": "nmf",               # NMF algorithm
       "LANGUAGE": "TR",                # Turkish language
       "separator": ",",                # CSV separator
       "gen_cloud": True,               # Generate word clouds
       "save_excel": True,              # Export to Excel
       "gen_topic_distribution": True   # Create distribution plots
   }
   
   # Run analysis
   result = run_standalone_nmf(
       filepath="data/turkish_reviews.csv",
       table_name="turkish_analysis",
       desired_columns="review_text",
       options=options
   )
   
   print(f"Analysis completed: {result['state']}")

English Text Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Configuration for English text
   options = {
       "LEMMATIZE": True,               # Enable lemmatization
       "N_TOPICS": 20,                  # Words per topic
       "DESIRED_TOPIC_COUNT": 8,        # Number of topics
       "tokenizer_type": None,          # Not used for English
       "nmf_type": "opnmf",             # Orthogonal NMF
       "LANGUAGE": "EN",                # English language
       "separator": ",",
       "gen_cloud": True,
       "save_excel": True,
       "gen_topic_distribution": True
   }
   
   # Run analysis
   result = run_standalone_nmf(
       filepath="data/english_documents.csv",
       table_name="english_analysis",
       desired_columns="content",
       options=options
   )

Input Data Format
----------------

Your CSV file should contain a text column for analysis:

.. code-block:: csv

   id,review_text,rating
   1,"This product is amazing! Love it.",5
   2,"Not satisfied with the quality.",2
   3,"Great value for money.",4

Output Files
-----------

The analysis generates several output files in the ``Output/{table_name}/`` directory:

- **Excel Report**: ``{table_name}_topics.xlsx`` - Topic-word matrices
- **Word Clouds**: ``wordclouds/Konu 01.png`` - Visual representations
- **Distribution Plot**: ``{table_name}_document_dist.png`` - Topic distribution
- **Coherence Scores**: ``{table_name}_coherence_scores.json`` - Quality metrics
- **Top Documents**: ``top_docs_{table_name}.json`` - Representative documents

Next Steps
----------

- Explore :doc:`configuration` for detailed parameter explanations
- Check :doc:`../examples/turkish_analysis` for advanced Turkish processing
- See :doc:`../examples/english_analysis` for English-specific features