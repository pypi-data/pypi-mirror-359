# NMF Standalone - Sphinx Documentation

This directory contains the modern Sphinx-based documentation for the NMF Standalone project.

## 🚀 Quick Start

### View Documentation
Open the generated documentation in your browser:

```bash
open docs/_build/html/index.html
```

Or visit: `file:///<path-to-project>/docs/_build/html/index.html`

### Build Documentation
To rebuild the documentation after making changes:

```bash
# Using the build script (recommended)
python build_docs.py

# Or directly with Sphinx
cd docs && uv run sphinx-build -b html . _build/html
```

## 📁 Documentation Structure

```
docs/
├── _build/html/          # Generated HTML documentation
├── _static/              # Custom CSS and static files
├── _templates/           # Custom HTML templates  
├── api/                  # API reference (manual)
├── usage/                # User guides
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
└── *.rst                # Auto-generated API docs
```

## 🎨 Features

### Modern Design
- **Read the Docs Theme**: Professional, responsive design
- **Dark/Light Mode**: Automatic theme switching
- **Mobile Friendly**: Works on all devices
- **Search**: Full-text search across all documentation

### Advanced Features
- **Auto-Generated API Docs**: Sphinx autodoc extracts docstrings automatically
- **Google-Style Docstrings**: Napoleon extension for clean parameter documentation
- **Cross-References**: Clickable links between functions and modules
- **Source Code Links**: Direct links to GitHub source code
- **Type Hints**: Enhanced type information display

### Documentation Sections
- **User Guide**: Installation, quickstart, configuration
- **API Reference**: Complete function and class documentation
- **Module Index**: Organized by functionality (Turkish/English/NMF/Utils)

## 🔧 Configuration

### Key Sphinx Extensions
- `sphinx.ext.autodoc` - Automatic API documentation
- `sphinx.ext.napoleon` - Google/NumPy docstring support
- `sphinx.ext.viewcode` - Source code links
- `sphinx_autodoc_typehints` - Enhanced type hint display
- `sphinx_rtd_theme` - Read the Docs theme

### Customization
- **Custom CSS**: `_static/custom.css` for additional styling
- **Theme Options**: Configured in `conf.py` for navigation depth, etc.
- **Mock Imports**: Heavy dependencies are mocked for faster builds

## 📝 Adding Documentation

### For New Functions
1. Add Google-style docstrings to your Python functions:
   ```python
   def my_function(param1: str, param2: int) -> bool:
       """
       Brief description of the function.
       
       Args:
           param1 (str): Description of parameter
           param2 (int): Description of parameter
       
       Returns:
           bool: Description of return value
       """
   ```

2. Rebuild documentation:
   ```bash
   python build_docs.py
   ```

### For New Sections
1. Create new `.rst` files in appropriate directories
2. Add to `toctree` in `index.rst` or relevant parent file
3. Rebuild documentation

## 🛠 Troubleshooting

### Common Issues

**Build Fails with Import Errors**
- Add problematic modules to `autodoc_mock_imports` in `conf.py`

**Missing Docstrings**
- Functions without docstrings appear but with minimal information
- Add Google-style docstrings for complete documentation

**Navigation Issues**
- Check `toctree` directives in `.rst` files
- Ensure file paths are correct in references

### Performance
- First build takes longer (generates all files)
- Subsequent builds are incremental and faster
- Use `-E` flag to force full rebuild when needed

## 📊 Generated Output

The current documentation includes:
- **91 HTML files** with comprehensive API coverage
- **All core modules** documented with docstrings
- **User guides** for installation and configuration
- **Cross-references** between related functions
- **Search index** for finding specific functions

## 🔄 Continuous Updates

The documentation automatically:
- Extracts docstrings from all Python modules
- Generates cross-references between functions
- Creates a searchable index
- Maintains consistent formatting

To keep documentation up to date:
1. Write docstrings for new functions
2. Run `python build_docs.py` 
3. Commit both source and generated files (optional)

## 📖 Comparison to Previous System

| Feature | Old (pydoc) | New (Sphinx) |
|---------|-------------|--------------|
| Theme | Basic HTML | Modern Read the Docs |
| Search | Browser only | Full-text search |
| Navigation | None | Hierarchical sidebar |
| Mobile | Poor | Responsive design |
| Cross-refs | Manual | Automatic |
| Type hints | Basic | Enhanced display |
| Customization | None | Highly customizable |

The new Sphinx system provides a professional, modern documentation experience that's on par with major Python projects like NumPy, SciPy, and Django.