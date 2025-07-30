#!/usr/bin/env python3
"""
NMF Standalone CLI Module

Command-line interfaces for the NMF topic modeling package.
"""

import argparse
import os
import sys
from pathlib import Path

# Handle imports for both development and installed package
try:
    # Try relative imports first (when installed as package)
    from .standalone_nmf import run_standalone_nmf
    from .coherence_eval_nmf import run_coherence_evaluation
    from .build_docs import main as build_docs_main
except ImportError:
    # Fall back to absolute imports (development mode)
    try:
        from standalone_nmf import run_standalone_nmf
        from coherence_eval_nmf import run_coherence_evaluation
        from build_docs import main as build_docs_main
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Make sure the package is properly installed or you're running from the project root.")
        sys.exit(1)


def main():
    """Main CLI entry point for NMF topic modeling."""
    parser = argparse.ArgumentParser(
        description="NMF Topic Modeling - Extract topics from text data using Non-negative Matrix Factorization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage for Turkish text
  nmf-standalone data.csv --column review_text --topics 5 --language TR
  
  # English text with custom output directory
  nmf-standalone data.csv --column text --topics 10 --language EN --output-dir results/
  
  # Advanced options with projective NMF
  nmf-standalone data.csv --column content --topics 8 --language TR --tokenizer bpe --nmf-type opnmf --gen-wordcloud
        """
    )
    
    # Required arguments
    parser.add_argument("input_file", help="Path to input CSV/Excel file")
    parser.add_argument("--column", "-c", required=True, help="Name of the column containing text to analyze")
    
    # Core parameters
    parser.add_argument("--topics", "-t", type=int, default=5, help="Number of topics to extract (default: 5)")
    parser.add_argument("--language", "-l", choices=["TR", "EN"], default="TR", 
                       help="Language of the text data (TR=Turkish, EN=English)")
    parser.add_argument("--tokenizer", choices=["bpe", "wordpiece"], default="bpe",
                       help="Tokenizer type for Turkish text (default: bpe)")
    parser.add_argument("--nmf-type", choices=["nmf", "opnmf"], default="nmf",
                       help="NMF algorithm type (nmf=standard, opnmf=projective)")
    
    # Output options
    parser.add_argument("--output-dir", "-o", default="./Output", 
                       help="Output directory for results (default: ./Output)")
    parser.add_argument("--gen-wordcloud", action="store_true", 
                       help="Generate word cloud visualizations")
    parser.add_argument("--save-excel", action="store_true", default=True,
                       help="Save results to Excel format (default: True)")
    parser.add_argument("--gen-topic-dist", action="store_true",
                       help="Generate topic distribution plots")
    
    # Advanced options
    parser.add_argument("--n-top-words", type=int, default=10,
                       help="Number of top words per topic (default: 10)")
    parser.add_argument("--lemmatize", action="store_true",
                       help="Enable lemmatization for English text")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    # Build options dictionary (matching the format expected by run_standalone_nmf)
    options = {
        'filepath': args.input_file,
        'desired_columns': args.column,
        'LANGUAGE': args.language,
        'DESIRED_TOPIC_COUNT': args.topics,
        'N_TOPICS': args.n_top_words,
        'tokenizer_type': args.tokenizer,
        'nmf_type': args.nmf_type,
        'gen_cloud': args.gen_wordcloud,
        'save_excel': args.save_excel,
        'gen_topic_distribution': args.gen_topic_dist,
        'LEMMATIZE': args.lemmatize if args.language == "EN" else False,
        'output_dir': args.output_dir
    }
    
    try:
        print(f"Starting NMF topic modeling...")
        print(f"Input: {args.input_file}")
        print(f"Column: {args.column}")
        print(f"Language: {args.language}")
        print(f"Topics: {args.topics}")
        print(f"Algorithm: {args.nmf_type}")
        print("-" * 50)
        
        run_standalone_nmf(options)
        print("\nTopic modeling completed successfully!")
        
    except Exception as e:
        print(f"Error during topic modeling: {str(e)}")
        sys.exit(1)


def coherence_main():
    """CLI entry point for coherence evaluation."""
    parser = argparse.ArgumentParser(
        description="NMF Coherence Evaluation - Find optimal number of topics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate topics from 2 to 15
  nmf-coherence data.csv --column review_text --min-topics 2 --max-topics 15
  
  # Turkish text with custom step size
  nmf-coherence data.csv --column text --language TR --min-topics 5 --max-topics 20 --step 2
        """
    )
    
    # Required arguments
    parser.add_argument("input_file", help="Path to input CSV/Excel file")
    parser.add_argument("--column", "-c", required=True, help="Name of the column containing text to analyze")
    
    # Topic range parameters
    parser.add_argument("--min-topics", type=int, default=2, help="Minimum number of topics (default: 2)")
    parser.add_argument("--max-topics", type=int, default=15, help="Maximum number of topics (default: 15)")
    parser.add_argument("--step", type=int, default=1, help="Step size for topic range (default: 1)")
    
    # Language and tokenizer options
    parser.add_argument("--language", "-l", choices=["TR", "EN"], default="TR",
                       help="Language of the text data (TR=Turkish, EN=English)")
    parser.add_argument("--tokenizer", choices=["bpe", "wordpiece"], default="bpe",
                       help="Tokenizer type for Turkish text (default: bpe)")
    
    # Output options
    parser.add_argument("--output-dir", "-o", default="./Output",
                       help="Output directory for results (default: ./Output)")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    # Validate topic range
    if args.min_topics >= args.max_topics:
        print("Error: min-topics must be less than max-topics.")
        sys.exit(1)
    
    # Build options dictionary
    options = {
        'filepath': args.input_file,
        'desired_columns': args.column,
        'LANGUAGE': args.language,
        'tokenizer_type': args.tokenizer,
        'min_topics': args.min_topics,
        'max_topics': args.max_topics,
        'step': args.step,
        'output_dir': args.output_dir
    }
    
    try:
        print(f"Starting coherence evaluation...")
        print(f"Input: {args.input_file}")
        print(f"Column: {args.column}")
        print(f"Language: {args.language}")
        print(f"Topic range: {args.min_topics}-{args.max_topics} (step: {args.step})")
        print("-" * 50)
        
        run_coherence_evaluation(options)
        print("\nCoherence evaluation completed successfully!")
        
    except Exception as e:
        print(f"Error during coherence evaluation: {str(e)}")
        sys.exit(1)


def docs_main():
    """CLI entry point for documentation building."""
    parser = argparse.ArgumentParser(
        description="Build NMF Standalone documentation using Sphinx"
    )
    
    parser.add_argument("--clean", action="store_true", 
                       help="Clean build directory before building")
    parser.add_argument("--open", action="store_true",
                       help="Open documentation in browser after building")
    
    args = parser.parse_args()
    
    try:
        print("Building documentation...")
        build_docs_main()
        
        if args.open:
            import webbrowser
            docs_path = Path("docs/_build/html/index.html")
            if docs_path.exists():
                webbrowser.open(f"file://{docs_path.absolute()}")
            else:
                print("Documentation built but HTML files not found at expected location.")
        
        print("Documentation build completed successfully!")
        
    except Exception as e:
        print(f"Error building documentation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()