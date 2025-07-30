"""
NMF Standalone - A comprehensive topic modeling library for Turkish and English texts.

This package provides Non-negative Matrix Factorization (NMF) based topic modeling
capabilities with support for both Turkish and English languages. It includes
advanced text preprocessing, multiple tokenization strategies, and comprehensive
visualization and export features.

Main Features:
- Support for Turkish and English text processing
- Multiple NMF algorithm variants (standard NMF and orthogonal projective NMF)
- Advanced tokenization (BPE, WordPiece for Turkish; traditional for English)
- Comprehensive text preprocessing and cleaning
- Word cloud generation and topic visualization
- Excel export and database storage
- Coherence score calculation for model evaluation

Example Usage:
    >>> from nmf_standalone import run_topic_analysis
    >>> result = run_topic_analysis(
    ...     "data.csv", 
    ...     column="text", 
    ...     language="TR", 
    ...     topics=5
    ... )
    >>> print(f"Found {len(result['topic_word_scores'])} topics")

Command Line Usage:
    $ nmf-standalone analyze data.csv --column text --language TR --topics 5 --wordclouds
"""

from .standalone_nmf import run_standalone_nmf, process_file
from .functions.common_language.emoji_processor import EmojiMap
from .functions.common_language.topic_analyzer import konu_analizi

# Version information
__version__ = "0.1.7"
__author__ = "Emir Kyz"
__email__ = "emirkyzmain@gmail.com"

# Public API exports
__all__ = [
    # Main functions
    "run_topic_analysis",
    "run_standalone_nmf", 
    "process_file",
    
    # Utility classes
    "EmojiMap",
    "konu_analizi",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
]


def run_topic_analysis(
    filepath: str,
    column: str,
    language: str = "TR",
    topics: int = 5,
    words_per_topic: int = 15,
    nmf_method: str = "nmf",
    tokenizer_type: str = "bpe",
    lemmatize: bool = False,
    generate_wordclouds: bool = True,
    export_excel: bool = True,
    topic_distribution: bool = True,
    output_name: str = None,
    **kwargs
):
    """
    High-level API for topic modeling analysis.
    
    This is a simplified interface to the full NMF standalone functionality,
    providing sensible defaults for common use cases.
    
    Args:
        filepath (str): Path to input CSV or Excel file
        column (str): Name of column containing text data
        language (str): "TR" for Turkish, "EN" for English
        topics (int): Number of topics to extract
        words_per_topic (int): Top words to show per topic
        nmf_method (str): "nmf" or "opnmf" algorithm variant
        tokenizer_type (str): "bpe" or "wordpiece" for Turkish
        lemmatize (bool): Apply lemmatization for English
        generate_wordclouds (bool): Create word cloud visualizations
        export_excel (bool): Export results to Excel
        topic_distribution (bool): Generate distribution plots
        output_name (str): Custom output directory name
        **kwargs: Additional options passed to underlying functions
        
    Returns:
        dict: Analysis results with topics and word scores
        
    Example:
        >>> result = run_topic_analysis(
        ...     "reviews.csv",
        ...     column="review_text", 
        ...     language="TR",
        ...     topics=7,
        ...     generate_wordclouds=True
        ... )
        >>> topics = result['topic_word_scores']
    """
    import os
    
    # Generate output name if not provided
    if output_name is None:
        filename = os.path.basename(filepath)
        base_name = os.path.splitext(filename)[0]
        output_name = f"{base_name}_{nmf_method}_{tokenizer_type}_{topics}"
    
    # Create emoji map
    emoji_map = EmojiMap()
    
    # Build options dictionary
    options = {
        "LANGUAGE": language.upper(),
        "DESIRED_TOPIC_COUNT": topics,
        "N_TOPICS": words_per_topic,
        "LEMMATIZE": lemmatize,
        "tokenizer_type": tokenizer_type,
        "tokenizer": None,
        "nmf_type": nmf_method,
        "separator": kwargs.get("separator", "|"),
        "gen_cloud": generate_wordclouds,
        "save_excel": export_excel,
        "gen_topic_distribution": topic_distribution,
        "filter_app": kwargs.get("filter_app", False),
        "filter_app_name": kwargs.get("filter_app_name", ""),
        "emoji_map": emoji_map
    }
    
    # Update with any additional kwargs
    options.update(kwargs)
    
    # Run the analysis
    return run_standalone_nmf(
        filepath=os.path.abspath(filepath),
        table_name=output_name,
        desired_columns=column,
        options=options
    )