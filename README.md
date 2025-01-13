# Project Mapper

A development tool that maintains up-to-date project documentation specifically designed for LLM-assisted development. It automatically tracks project structure and docstrings, maintaining a standardized `.cursorrules` file that can be included in every interaction with an LLM.

## Features

- Scans Python source files for structure and docstrings
- Maintains project structure map in `.cursorrules` XML file
- Extensible template system with base rules and language-specific extensions
- Command-line interface for easy project setup and scanning

## Requirements

- Python 3.9+
- Git repository

## Installation

```bash
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Setup templates (do this first)
project-mapper --setup-templates

# Scan project and update documentation
project-mapper

# Use specific templates
project-mapper --base-template base --extension-template python

# Scan a different directory
project-mapper --project-root /path/to/project

# Enable debug logging
project-mapper --debug

# Install git hooks (coming soon)
project-mapper --install-hooks
```

All options:
```
--project-root, -p    Project root directory (default: current directory)
--language, -l        Project language (default: python)
--base-template, -b   Base template name to use
--extension-template, -e  Extension template name to use
--install-hooks      Install git hooks
--setup-templates    Setup or change templates
--debug             Enable debug logging
```

### Template System

Project Mapper uses an extensible template system:

1. Base Template (`base.xml`): Contains core documentation rules
   - File-level docstring format
   - Documentation maintenance guidelines
   - Project structure mapping

2. Language Extensions: Add language-specific rules
   - Python extension adds:
     - Google style docstring format
     - Type hint requirements
     - Import organization rules

Templates are stored in `.project-mapper/templates/` in your project root.

### Python API

```python
from project_mapper import PythonScanner, XMLManager
from pathlib import Path

# Initialize components
project_root = Path.cwd()
scanner = PythonScanner(project_root)
xml_manager = XMLManager(project_root)

# Scan project and update documentation
structure = scanner.scan_project()
xml_manager.update_project_map(structure)
```

## Development

Current focus areas:
- Git hook integration for automatic updates
- Additional language support
- Enhanced template customization
- Multiple extension support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the project's Python style guide:
   - Google style docstrings
   - Type hints for parameters and return values
   - Organized imports (stdlib, third-party, local)
4. Submit a pull request

## License

MIT 