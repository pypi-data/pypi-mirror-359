#!/usr/bin/env python3
"""
NMF Standalone CLI - Command-line interface for NMF topic modeling.

This module provides CLI entry points for the nmf-standalone package.
"""

import argparse
import sys
import os
from pathlib import Path

# Handle both development and installed package imports
try:
    # Try importing from installed package
    from __init__ import run_standalone_nmf, run_coherence_evaluation, build_documentation
    from __init__ import EmojiMap
except ImportError:
    # Fall back to development imports
    try:
        from standalone_nmf import run_standalone_nmf
        from coherence_eval_nmf import run_coherence_evaluation  
        from build_docs import main as build_documentation
        from functions.common_language.emoji_processor import EmojiMap
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure nmf-standalone is properly installed.")
        sys.exit(1)


def main():
    """Main CLI entry point for NMF topic modeling."""
    parser = argparse.ArgumentParser(
        description="NMF Standalone - Topic modeling using Non-negative Matrix Factorization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nmf-standalone --file data.csv --column text --language TR --topics 5
  nmf-standalone --file data.xlsx --column content --language EN --topics 10 --lemmatize
  nmf-standalone --file reviews.csv --column review_text --language TR --topics 8 --tokenizer bpe
        """
    )
    
    # Required arguments
    parser.add_argument('--file', '-f', required=True,
                        help='Path to input CSV or Excel file')
    parser.add_argument('--column', '-c', required=True,
                        help='Name of the column containing text data')
    parser.add_argument('--language', '-l', required=True, choices=['TR', 'EN'],
                        help='Language of the text data (TR for Turkish, EN for English)')
    parser.add_argument('--topics', '-t', type=int, required=True,
                        help='Number of topics to extract')
    
    # Optional arguments
    parser.add_argument('--table-name', default=None,
                        help='Name for the analysis (default: auto-generated from filename)')
    parser.add_argument('--top-words', type=int, default=15,
                        help='Number of top words to display per topic (default: 15)')
    parser.add_argument('--nmf-type', choices=['nmf', 'opnmf'], default='nmf',
                        help='NMF algorithm type (default: nmf)')
    parser.add_argument('--tokenizer', choices=['bpe', 'wordpiece'],
                        help='Tokenizer type for Turkish (default: bpe)')
    parser.add_argument('--lemmatize', action='store_true',
                        help='Enable lemmatization for English text')
    parser.add_argument('--separator', default=',',
                        help='CSV separator (default: comma)')
    parser.add_argument('--no-wordcloud', action='store_true',
                        help='Disable word cloud generation')
    parser.add_argument('--no-excel', action='store_true', 
                        help='Disable Excel output')
    parser.add_argument('--no-plots', action='store_true',
                        help='Disable topic distribution plots')
    parser.add_argument('--filter-app', 
                        help='Filter data by application name')
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    
    # Generate table name if not provided
    if args.table_name is None:
        file_stem = Path(args.file).stem
        args.table_name = f"{file_stem}_{args.language.lower()}_{args.nmf_type}_{args.topics}"
    
    # Build options dictionary
    options = {
        "LANGUAGE": args.language,
        "DESIRED_TOPIC_COUNT": args.topics,
        "N_TOPICS": args.top_words,
        "nmf_type": args.nmf_type,
        "separator": args.separator,
        "gen_cloud": not args.no_wordcloud,
        "save_excel": not args.no_excel,
        "gen_topic_distribution": not args.no_plots,
        "filter_app": bool(args.filter_app),
        "filter_app_name": args.filter_app or "",
        "LEMMATIZE": args.lemmatize if args.language == "EN" else False,
        "tokenizer_type": args.tokenizer if args.language == "TR" else None,
        "tokenizer": None,
        "emoji_map": EmojiMap() if args.language == "TR" else None
    }
    
    print(f"Starting NMF topic modeling...")
    print(f"File: {args.file}")
    print(f"Column: {args.column}")
    print(f"Language: {args.language}")
    print(f"Topics: {args.topics}")
    print(f"Algorithm: {args.nmf_type}")
    
    try:
        run_standalone_nmf(
            filepath=args.file,
            table_name=args.table_name,
            desired_columns=args.column,
            options=options
        )
        print(f"\\nTopic modeling completed successfully!")
        print(f"Results saved with table name: {args.table_name}")
    except Exception as e:
        print(f"Error during topic modeling: {e}")
        sys.exit(1)


def coherence_main():
    """CLI entry point for coherence evaluation."""
    parser = argparse.ArgumentParser(
        description="NMF Coherence Evaluation - Find optimal number of topics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--file', '-f', required=True,
                        help='Path to input CSV or Excel file')
    parser.add_argument('--column', '-c', required=True,
                        help='Name of the column containing text data')
    parser.add_argument('--language', '-l', required=True, choices=['TR', 'EN'],
                        help='Language of the text data')
    parser.add_argument('--min-topics', type=int, default=2,
                        help='Minimum number of topics to test (default: 2)')
    parser.add_argument('--max-topics', type=int, default=20,
                        help='Maximum number of topics to test (default: 20)')
    parser.add_argument('--step', type=int, default=1,
                        help='Step size for topic range (default: 1)')
    parser.add_argument('--metric', choices=['c_v', 'u_mass'], default='c_v',
                        help='Coherence metric to use (default: c_v)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    
    print(f"Starting coherence evaluation...")
    print(f"Topics range: {args.min_topics}-{args.max_topics} (step: {args.step})")
    print(f"Metric: {args.metric}")
    
    try:
        run_coherence_evaluation(
            filepath=args.file,
            column=args.column,
            language=args.language,
            min_topics=args.min_topics,
            max_topics=args.max_topics,
            step=args.step,
            metric=args.metric
        )
        print("\\nCoherence evaluation completed!")
    except Exception as e:
        print(f"Error during coherence evaluation: {e}")
        sys.exit(1)


def docs_main():
    """CLI entry point for documentation building."""
    parser = argparse.ArgumentParser(
        description="Build NMF Standalone documentation"
    )
    
    parser.add_argument('--output-dir', default='docs/_build',
                        help='Output directory for documentation (default: docs/_build)')
    parser.add_argument('--format', choices=['html', 'pdf'], default='html',
                        help='Documentation format (default: html)')
    
    args = parser.parse_args()
    
    print("Building documentation...")
    
    try:
        build_documentation(
            output_dir=args.output_dir,
            format=args.format
        )
        print(f"\\nDocumentation built successfully in {args.output_dir}")
    except Exception as e:
        print(f"Error building documentation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()