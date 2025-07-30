NMF Standalone Documentation
============================

Welcome to the **NMF Standalone** documentation. This project provides a comprehensive topic modeling system using Non-negative Matrix Factorization (NMF) for both Turkish and English languages.

Overview
--------

NMF Standalone is a complete end-to-end topic modeling pipeline that includes:

* **Bilingual Support**: Advanced text processing for Turkish and English
* **Multiple Tokenization Methods**: BPE and WordPiece tokenizers for Turkish
* **Flexible NMF Algorithms**: Standard NMF and Orthogonal Projective NMF (OPNMF)
* **Rich Visualizations**: Word clouds, topic distributions, and coherence analysis
* **Multiple Output Formats**: Excel reports, JSON data, and PNG visualizations

Quick Start
-----------

.. code-block:: python

   from standalone_nmf import run_standalone_nmf
   
   options = {
       "LANGUAGE": "TR",
       "DESIRED_TOPIC_COUNT": 5,
       "N_TOPICS": 15,
       "tokenizer_type": "bpe",
       "nmf_type": "nmf",
       "gen_cloud": True,
       "save_excel": True,
   }
   
   result = run_standalone_nmf(
       filepath="data.csv",
       table_name="analysis",
       desired_columns="text",
       options=options
   )

Documentation Sections
----------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   usage/installation
   usage/quickstart
   usage/configuration

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   standalone_nmf
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`