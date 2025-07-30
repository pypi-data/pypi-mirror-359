# NMF Standalone

[![PyPI version](https://badge.fury.io/py/nmf-standalone.svg)](https://badge.fury.io/py/nmf-standalone)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive topic modeling system using Non-negative Matrix Factorization (NMF) that supports both English and Turkish text processing. Features advanced tokenization techniques, multiple NMF algorithms, and rich visualization capabilities.

## Quick Start

### Installation from PyPI

```bash
pip install nmf-standalone
```

### Command Line Usage

```bash
# Turkish text analysis
nmf-standalone --file data.csv --column text --language TR --topics 5

# English text analysis with lemmatization
nmf-standalone --file data.csv --column content --language EN --topics 10 --lemmatize

# Coherence evaluation to find optimal topic count
nmf-coherence --file data.csv --column text --language TR --min-topics 2 --max-topics 15
```

### Python API Usage

```python
import nmf_standalone

# Run topic modeling
nmf_standalone.run_standalone_nmf(
    filepath="data.csv",
    table_name="my_analysis", 
    desired_columns="text_column",
    options={
        "LANGUAGE": "TR",
        "DESIRED_TOPIC_COUNT": 5,
        "nmf_type": "nmf"
    }
)
```

## Project Structure

```
nmf-standalone/
├── functions/
│   ├── common_language/          # Shared functionality across languages
│   │   ├── emoji_processor.py    # Emoji handling utilities
│   │   └── topic_analyzer.py     # Cross-language topic analysis
│   ├── english/                  # English text processing modules
│   │   ├── english_preprocessor.py      # Text cleaning and preprocessing
│   │   ├── english_vocabulary.py        # Vocabulary creation
│   │   ├── english_text_encoder.py      # Text-to-numerical conversion
│   │   ├── english_topic_analyzer.py    # Topic extraction utilities
│   │   ├── english_topic_output.py      # Topic visualization and output
│   │   └── english_nmf_core.py          # NMF implementation for English
│   ├── nmf/                      # NMF algorithm implementations
│   │   ├── nmf_orchestrator.py          # Main NMF interface
│   │   ├── nmf_initialization.py        # Matrix initialization strategies
│   │   ├── nmf_multiplicative_updates.py # Standard NMF algorithm
│   │   ├── nmf_projective_basic.py      # Basic projective NMF
│   │   └── nmf_projective_enhanced.py   # Enhanced projective NMF
│   ├── tfidf/                    # TF-IDF calculation modules
│   │   ├── tfidf_english_calculator.py  # English TF-IDF implementation
│   │   ├── tfidf_turkish_calculator.py  # Turkish TF-IDF implementation
│   │   ├── tfidf_tf_functions.py        # Term frequency functions
│   │   ├── tfidf_idf_functions.py       # Inverse document frequency functions
│   │   └── tfidf_bm25_turkish.py        # BM25 implementation for Turkish
│   └── turkish/                  # Turkish text processing modules
│       ├── turkish_preprocessor.py      # Turkish text cleaning
│       ├── turkish_tokenizer_factory.py # Tokenizer creation and training
│       ├── turkish_text_encoder.py      # Text-to-numerical conversion
│       └── turkish_tfidf_generator.py   # TF-IDF matrix generation
├── utils/                        # Helper utilities
│   ├── other/
├── veri_setleri/                 # Input datasets directory
├── instance/                     # Database storage
├── Output/                       # Generated outputs
├── pyproject.toml
├── README.md
├── requirements.txt
├── standalone_nmf.py
└── uv.lock
```

-   **`functions/`**: Contains the core logic for the NMF pipeline with a well-organized structure:
    -   **`common_language/`**: Shared functionality that works across both languages (emoji processing, topic analysis)
    -   **`english/`**: English-specific text processing modules with descriptive names
    -   **`turkish/`**: Turkish-specific text processing modules with descriptive names  
    -   **`nmf/`**: NMF algorithm implementations (standard, projective, initialization strategies)
    -   **`tfidf/`**: TF-IDF calculation modules for both languages with various weighting schemes
-   **`utils/`**: Includes helper functions for tasks like generating word clouds, calculating coherence scores, and exporting results.
-   **`veri_setleri/`**: Default directory for input datasets.
-   **`instance/`**: Stores databases created during the process (e.g., `topics.db`, `scopus.db`).
-   **`Output/`**: Directory where all the output files, such as topic reports, word clouds, and distribution plots, are saved.
-   **`standalone_nmf.py`**: The main executable script to run the topic modeling process.
-   **`requirements.txt`**: A list of Python packages required for the project.

## File Naming Convention

This project follows a consistent and descriptive naming convention to improve code organization and readability:

### Language-Specific Modules
- **English modules**: `english_{functionality}.py` (e.g., `english_preprocessor.py`, `english_vocabulary.py`)
- **Turkish modules**: `turkish_{functionality}.py` (e.g., `turkish_preprocessor.py`, `turkish_tokenizer_factory.py`)

### Algorithm and Utility Modules
- **NMF algorithms**: `nmf_{algorithm_type}.py` (e.g., `nmf_orchestrator.py`, `nmf_projective_basic.py`)
- **TF-IDF modules**: `tfidf_{functionality}.py` (e.g., `tfidf_english_calculator.py`, `tfidf_tf_functions.py`)

### Shared Functionality
- **Common language modules**: Located in `common_language/` for cross-language functionality (e.g., `emoji_processor.py`, `topic_analyzer.py`)

This naming convention replaces the previous mixed Turkish/English naming (e.g., `sozluk.py` → `english_vocabulary.py`, `temizle.py` → `turkish_preprocessor.py`) making the codebase more accessible and self-documenting.

## Installation

### From PyPI (Recommended)

```bash
pip install nmf-standalone
```

### From Source (Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/nmf-standalone.git
   cd nmf-standalone
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install with uv (recommended):**
   ```bash
   uv pip install -r requirements.txt
   ```

   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

After installation, you have access to three command-line tools:

#### 1. Topic Modeling (`nmf-standalone`)

```bash
# Basic usage
nmf-standalone --file data.csv --column text --language TR --topics 5

# Advanced usage with all options
nmf-standalone \
  --file reviews.csv \
  --column review_text \
  --language EN \
  --topics 10 \
  --top-words 20 \
  --nmf-type opnmf \
  --lemmatize \
  --no-wordcloud \
  --table-name my_analysis
```

#### 2. Coherence Evaluation (`nmf-coherence`)

Find the optimal number of topics:

```bash
nmf-coherence \
  --file data.csv \
  --column text \
  --language TR \
  --min-topics 2 \
  --max-topics 15 \
  --metric c_v
```

#### 3. Documentation Builder (`nmf-docs`)

```bash
nmf-docs --output-dir ./docs --format html
```

### Python API

```python
import nmf_standalone

# Basic usage
nmf_standalone.run_standalone_nmf(
    filepath="data.csv",
    table_name="my_analysis",
    desired_columns="text_column",
    options={
        "LANGUAGE": "TR",
        "DESIRED_TOPIC_COUNT": 5,
        "nmf_type": "nmf",
        "gen_cloud": True,
        "save_excel": True
    }
)

# Advanced usage with Turkish text
from nmf_standalone import EmojiMap

turkish_options = {
    "LANGUAGE": "TR",
    "DESIRED_TOPIC_COUNT": 10,
    "N_TOPICS": 15,
    "tokenizer_type": "bpe",
    "nmf_type": "nmf",
    "gen_cloud": True,
    "save_excel": True,
    "gen_topic_distribution": True,
    "emoji_map": EmojiMap()
}

nmf_standalone.run_standalone_nmf(
    filepath="turkish_reviews.csv",
    table_name="turkish_analysis",
    desired_columns="review_text",
    options=turkish_options
)
```

### Parameters

The `run_standalone_nmf` function takes the following parameters:

-   `filepath`: Path to your input `.csv` or `.xlsx` file.
-   `table_name`: A unique name for your analysis run. This is used for naming output files and database tables.
-   `desired_columns`: The name of the column in your data file that contains the text to be analyzed.
-   `options`: A dictionary containing all configuration options:

#### Options Dictionary Structure

**Core Parameters:**
-   `LANGUAGE`: `"TR"` for Turkish or `"EN"` for English.
-   `DESIRED_TOPIC_COUNT`: The number of topics to extract.
-   `N_TOPICS`: The number of top words to display for each topic.
-   `nmf_type`: The NMF algorithm to use (`"nmf"` or `"opnmf"`).

**Language-Specific Parameters:**
-   `LEMMATIZE`: Set to `True` for English text to enable lemmatization (ignored for Turkish).
-   `tokenizer_type`: For Turkish, choose between `"bpe"` (Byte-Pair Encoding) or `"wordpiece"`.
-   `tokenizer`: Pre-initialized tokenizer instance (optional, set to `None` for auto-initialization).
-   `emoji_map`: EmojiMap instance for Turkish emoji processing (use `EmojiMap()` for Turkish, `None` for English).

**File Processing Parameters:**
-   `separator`: The separator used in your `.csv` file (e.g., `,`, `;`).
-   `filter_app`: Set to `True` to filter data by application name.
-   `filter_app_name`: Application name to filter by (when `filter_app` is `True`).

**Output Generation Parameters:**
-   `gen_cloud`: Set to `True` to generate word cloud images for each topic.
-   `save_excel`: Set to `True` to export results to Excel format.
-   `gen_topic_distribution`: Set to `True` to generate topic distribution plots.

## Outputs

The script generates several outputs in the `Output/` directory, organized in a subdirectory named after your `table_name`:

-   **Topic-Word Excel File**: An `.xlsx` file containing the top words for each topic and their scores.
-   **Word Clouds**: PNG images of word clouds for each topic.
-   **Topic Distribution Plot**: A plot showing the distribution of documents across topics.
-   **Coherence Scores**: A JSON file with coherence scores for the topics.
-   **Top Documents**: A JSON file listing the most representative documents for each topic.
