# LLM Project Companion

A development tool that maintains up-to-date project documentation specifically designed for LLM-assisted development. It automatically tracks project structure and docstrings, maintaining a standardized `.cursorrules` file that can be included in every interaction with an LLM.

## Features (v0.0.1)

- Scans Python source files for structure and docstrings
- Maintains project structure map in `.cursorrules` XML file
- Automatic updates via git hooks (coming soon)

## Requirements

- Python 3.9+
- Git repository

## Installation

```bash
pip install -e .
```

## Usage

```python
from llm_companion import ProjectScanner
from pathlib import Path

# Initialize scanner with project root
scanner = ProjectScanner(Path.cwd())

# Scan project and update .cursorrules
structure = scanner.scan_project()
scanner.update_cursorrules(structure)
```

## Development

This is an early version (0.0.1) focused on core functionality. Future versions will include:
- Git hook integration
- Enhanced docstring validation
- Additional file type support
- Customizable rule sections 