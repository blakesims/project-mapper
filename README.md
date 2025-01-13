# Project Mapper

A development tool that maintains up-to-date project documentation specifically designed for LLM-assisted development. It automatically tracks project structure and docstrings, maintaining a standardized `.cursorrules` file that can be included in every interaction with an LLM.
Note: only working for python at the moment, typescript is next on the list.

## Features

- Scans Python source files for structure and docstrings
- Maintains project structure map in `.cursorrules` XML file
- Extensible template system with base rules and language-specific extensions
- Command-line interface for easy project setup and scanning
- Automatic updates via git pre-commit hook - if changes in docstrings is noticed, or files removed, the cursorrules project map will be updated and included in the commit automatically
- Smart directory exclusion (respects .gitignore patterns and common ignore paths)
- Template updates with change preview and safe handling of local modifications

## Requirements

- Python 3.9+
- Git repository

## Installation

### Global Installation
```bash
pip install -e .
```

### Virtual Environment Installation
If your project uses a virtual environment (recommended), activate it first and then install:

```bash
# Create and activate virtual environment (if not already done)
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows

# Install project-mapper in the virtual environment
pip install -e /path/to/project-mapper

# Verify installation
which project-mapper  # Should show path inside your venv
project-mapper --version
```

Note: Replace `/path/to/project-mapper` with the actual path to where you've cloned the project-mapper repository.

## Usage

### Command Line Interface

Important: update your cursorrules file first.

```bash
# Setup templates (do this first)
project-mapper --setup-templates

# Check for and apply template updates
project-mapper --update-templates

# Scan project and update documentation
project-mapper

# Use specific templates
project-mapper --base-template base --extension-template python

# Scan a different directory
project-mapper --project-root /path/to/project

# Enable debug logging
project-mapper --debug

# Install git hooks (automatically updates .cursorrules on commit)
project-mapper --install-hooks
```

All options:

```
--project-root, -p    Project root directory (default: current directory)
--language, -l        Project language (default: python)
--base-template, -b   Base template name to use
--extension-template, -e  Extension template name to use
--install-hooks      Install git hooks for automatic updates
--setup-templates    Setup or change templates
--update-templates   Check for and apply template updates
--debug             Enable debug logging
```

### Directory Exclusions

Project Mapper automatically excludes files and directories based on:

1. Your project's `.gitignore` patterns
2. Common Python ignore patterns:
   - Virtual environments (`venv`, `.venv`, `env`, etc.)
   - Python cache files (`*.py[cod]`, `__pycache__/`)
   - Build directories (`dist/`, `build/`, `*.egg-info/`)
   - C extensions (`*.so`)

This ensures that only your project's source code is documented, not its dependencies, build artifacts, or ignored files.

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

#### Updating Templates

You can check for and apply template updates using:

```bash
project-mapper --update-templates
```

This will:
1. Check for available updates in the template repository
2. Show you what files will be modified, added, or deleted
3. Warn about any local template modifications
4. Let you choose whether to apply the updates

If you have local template modifications:
- They will be shown in the update preview
- You'll be warned that they will be lost if you update
- You can choose to skip the update to preserve your changes

### Git Integration

Project Mapper automatically updates your documentation on each commit through a git pre-commit hook. This ensures your `.cursorrules` file is always in sync with your codebase.

The hook:

1. Runs before each commit
2. Updates the project documentation
3. Adds the updated `.cursorrules` file to the commit

To install the hook:

```bash
project-mapper --install-hooks
```

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

- Additional language support
- Enhanced template customization
- Multiple extension support
- Additional git hook types (post-merge, post-checkout)

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

