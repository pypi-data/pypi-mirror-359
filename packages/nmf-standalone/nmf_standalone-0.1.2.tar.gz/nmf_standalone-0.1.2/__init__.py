"""
NMF Standalone - A comprehensive NMF topic modeling system

A Python package for topic modeling using Non-negative Matrix Factorization (NMF)
with support for both Turkish and English text processing.

Key Features:
- Turkish and English text preprocessing
- Multiple NMF algorithms (standard and projective)
- TF-IDF vectorization with language-specific optimizations
- Coherence evaluation for optimal topic selection
- Word cloud generation and visualization
- Excel export and database storage
"""

__version__ = "0.1.2"
__author__ = "Emir Karayagiz"
__email__ = "emirkyzmain@gmail.com"

# Import core functions and make them available at package level
try:
    # When installed as package, import with package prefix
    from .standalone_nmf import run_standalone_nmf, process_file
    from .coherence_eval_nmf import run_coherence_evaluation  
    from .build_docs import main as build_docs
except ImportError:
    # Fallback for development mode
    try:
        from standalone_nmf import run_standalone_nmf, process_file
        from coherence_eval_nmf import run_coherence_evaluation
        from build_docs import main as build_docs
    except ImportError:
        # Create stub functions if imports fail
        def run_standalone_nmf(*args, **kwargs):
            raise ImportError("nmf-standalone package not properly installed. Please reinstall with: pip install --force-reinstall nmf-standalone")
        
        def run_coherence_evaluation(*args, **kwargs):
            raise ImportError("nmf-standalone package not properly installed. Please reinstall with: pip install --force-reinstall nmf-standalone")
        
        def build_docs(*args, **kwargs):
            raise ImportError("nmf-standalone package not properly installed. Please reinstall with: pip install --force-reinstall nmf-standalone")
        
        process_file = None

# Import utilities and function modules
try:
    # When installed as package
    from .functions.nmf.nmf_orchestrator import run_nmf
    from .functions.common_language.emoji_processor import EmojiMap
    from .functions.common_language.topic_analyzer import konu_analizi
    from .utils.coherence_score import calculate_coherence_scores
    from .utils.export_excel import export_topics_to_excel
    from .utils.gen_cloud import generate_wordclouds
except ImportError:
    # Fallback for development mode
    try:
        from functions.nmf.nmf_orchestrator import run_nmf
        from functions.common_language.emoji_processor import EmojiMap
        from functions.common_language.topic_analyzer import konu_analizi
        from utils.coherence_score import calculate_coherence_scores
        from utils.export_excel import export_topics_to_excel
        from utils.gen_cloud import generate_wordclouds
    except ImportError:
        # Create stubs if utilities can't be imported
        run_nmf = None
        EmojiMap = None
        konu_analizi = None
        calculate_coherence_scores = None
        export_topics_to_excel = None
        generate_wordclouds = None

__all__ = [
    # Core functions
    "run_standalone_nmf",
    "process_file", 
    "run_coherence_evaluation",
    "build_docs",
    
    # NMF and analysis
    "run_nmf",
    "EmojiMap",
    "konu_analizi",
    
    # Utilities
    "calculate_coherence_scores",
    "export_topics_to_excel", 
    "generate_wordclouds",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
]