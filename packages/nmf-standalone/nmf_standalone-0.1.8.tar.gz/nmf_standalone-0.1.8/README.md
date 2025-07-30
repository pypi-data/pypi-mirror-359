# NMF Standalone

A comprehensive topic modeling library for Turkish and English texts using Non-negative Matrix Factorization (NMF).

## Features

- **Multi-language Support**: Native support for Turkish and English text processing
- **Advanced NMF Algorithms**: Standard NMF and Orthogonal Projective NMF (OPNMF) variants
- **Modern Tokenization**: BPE and WordPiece tokenizers for Turkish, traditional preprocessing for English
- **Comprehensive Preprocessing**: Language-specific text cleaning, emoji processing, and normalization
- **Rich Visualizations**: Word clouds, topic distribution plots, and co-occurrence heatmaps
- **Multiple Export Formats**: Excel reports, JSON results, and database storage
- **Coherence Evaluation**: Built-in topic coherence scoring for model evaluation
- **CLI and Python API**: Both command-line interface and programmatic access

## Installation

```bash
pip install nmf-standalone
```

For visualization features:
```bash
pip install nmf-standalone[visualization]
```

## Quick Start

### Command Line Interface

```bash
# Analyze Turkish app reviews with 5 topics
nmf-standalone analyze reviews.csv --column REVIEW --language TR --topics 5 --wordclouds

# Analyze English documents with lemmatization
nmf-standalone analyze docs.xlsx --column text --language EN --topics 10 --lemmatize --excel

# Use BPE tokenizer for Turkish text
nmf-standalone analyze data.csv --column content --language TR --tokenizer bpe --topics 7
```

### Python API

```python
from nmf_standalone import run_topic_analysis

# Simple analysis
result = run_topic_analysis(
    "data.csv",
    column="text_column", 
    language="TR",
    topics=5,
    generate_wordclouds=True
)

# Access results
topics = result['topic_word_scores']
for topic_id, words in topics.items():
    print(f"Topic {topic_id}: {', '.join([word for word, score in words[:5]])}")

# Advanced configuration
result = run_topic_analysis(
    "reviews.csv",
    column="review_text",
    language="TR", 
    topics=7,
    nmf_method="opnmf",  # Use projective NMF
    tokenizer_type="wordpiece",
    words_per_topic=20,
    export_excel=True,
    topic_distribution=True
)
```

## Supported File Formats

- **CSV files**: Automatic delimiter detection, UTF-8 encoding
- **Excel files**: .xlsx and .xls formats
- **Text columns**: Any column containing text data for analysis

## Language Support

### Turkish
- **Preprocessing**: Advanced text cleaning, Turkish-specific normalization
- **Tokenization**: BPE (Byte-Pair Encoding) and WordPiece tokenizers
- **Emoji Processing**: Intelligent emoji-to-text conversion
- **TF-IDF**: BM25 and traditional TF-IDF with Turkish language adaptations

### English  
- **Preprocessing**: Standard NLP preprocessing with optional lemmatization
- **Tokenization**: Traditional word-based tokenization
- **Lemmatization**: NLTK-based lemmatization support
- **TF-IDF**: Classical TF-IDF with multiple weighting schemes

## Algorithm Options

### NMF Methods
- **Standard NMF** (`nmf`): Classical non-negative matrix factorization
- **Orthogonal Projective NMF** (`opnmf`): Enhanced variant for better topic separation

### Tokenization (Turkish)
- **BPE** (`bpe`): Byte-Pair Encoding for subword tokenization
- **WordPiece** (`wordpiece`): Google's WordPiece algorithm

## Output Formats

### Generated Files
- **Word Clouds**: PNG images for each topic showing prominent words
- **Excel Reports**: Detailed topic-word matrices with scores
- **Topic Distribution**: Plots showing document-topic relationships
- **JSON Results**: Machine-readable topic and document data
- **Database Storage**: SQLite databases for persistent storage

### Directory Structure
```
Output/
└── {dataset_name}/
    ├── {dataset}_topics.xlsx           # Excel report
    ├── {dataset}_coherence_scores.json # Model evaluation
    ├── {dataset}_document_dist.png     # Topic distribution
    ├── top_docs_{dataset}.json         # Top documents per topic
    └── wordclouds/                     # Word cloud images
        ├── Topic_00.png
        ├── Topic_01.png
        └── ...
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topics` | int | 5 | Number of topics to extract |
| `words_per_topic` | int | 15 | Top words to display per topic |
| `language` | str | "TR" | Language code (TR/EN) |
| `nmf_method` | str | "nmf" | Algorithm variant (nmf/opnmf) |
| `tokenizer_type` | str | "bpe" | Tokenizer for Turkish (bpe/wordpiece) |
| `lemmatize` | bool | False | Apply lemmatization (English only) |
| `generate_wordclouds` | bool | True | Create word cloud visualizations |
| `export_excel` | bool | True | Export Excel reports |
| `topic_distribution` | bool | True | Generate distribution plots |

## Requirements

- Python ≥ 3.8
- NumPy ≥ 1.24.0
- Pandas ≥ 2.0.0
- scikit-learn ≥ 1.3.0
- NLTK ≥ 3.8.0
- gensim ≥ 4.3.0
- tokenizers ≥ 0.19.0

## Examples

### Turkish App Review Analysis
```python
result = run_topic_analysis(
    "app_reviews.csv",
    column="review_text",
    language="TR",
    topics=8,
    tokenizer_type="bpe",
    generate_wordclouds=True,
    export_excel=True
)
```

### English Document Classification
```python
result = run_topic_analysis(
    "documents.xlsx", 
    column="content",
    language="EN",
    topics=12,
    lemmatize=True,
    nmf_method="opnmf",
    words_per_topic=25
)
```

### Medical Text Analysis
```python
result = run_topic_analysis(
    "medical_notes.csv",
    column="impression", 
    language="EN",
    topics=15,
    lemmatize=True,
    generate_wordclouds=True,
    topic_distribution=True
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{nmf_standalone,
  author = {Emir Karayagiz},
  title = {NMF Standalone: Topic Modeling for Turkish and English Texts},
  url = {https://github.com/emirkarayagiz/nmf-standalone},
  version = {0.1.0},
  year = {2024}
}
```