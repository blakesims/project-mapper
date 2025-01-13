"""Python-specific implementation of project scanner."""

import ast
from pathlib import Path
from typing import Dict, List, Optional

import pathspec

from ..base import BaseAdapter

# Common virtual environment directory names
VENV_DIRS = {"venv", "env", ".env", ".venv", "virtualenv", ".virtualenv"}


class PythonScanner(BaseAdapter):
    """Scanner implementation for Python projects."""

    def __init__(self, project_root: Path):
        """Initialize scanner with project root.

        Args:
            project_root: Root directory of the project
        """
        super().__init__(project_root)
        self.ignore_spec = self._load_ignore_patterns()

    def _load_ignore_patterns(self) -> pathspec.PathSpec:
        """Load patterns from both .gitignore and .projectmapperignore files.

        Returns:
            PathSpec object for matching against combined ignore patterns
        """
        patterns = []

        # Load .gitignore patterns
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                patterns.extend(
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                )

        # Load .projectmapperignore patterns
        projectmapper_ignore_path = self.project_root / ".projectmapperignore"
        if projectmapper_ignore_path.exists():
            with open(projectmapper_ignore_path) as f:
                patterns.extend(
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                )

        # Add default Python patterns if not already in patterns
        default_patterns = {
            "*.py[cod]",  # Python bytecode
            "__pycache__/",
            "*.so",  # C extensions
            "dist/",
            "build/",
            "*.egg-info/",
        }
        patterns.extend(p for p in default_patterns if p not in patterns)

        return pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, patterns
        )

    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file is a Python source file.

        Args:
            file_path: Path to check

        Returns:
            True if file is a .py file and not a special file
        """
        # Check if file is in a virtual environment directory
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts

            # Check virtual env directories
            if any(part in VENV_DIRS for part in parts):
                return False

            # Check combined ignore patterns
            if self.ignore_spec.match_file(str(rel_path)):
                return False

        except ValueError:
            # If file is not under project root, skip it
            return False

        return file_path.suffix == ".py" and not file_path.name.startswith("__")

    def extract_documentation(self, file_path: Path) -> Dict:
        """Extract documentation from Python source file.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary containing:
            - purpose: Full module docstring
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            # Get full module docstring
            module_doc = ast.get_docstring(tree) or "No description available"

            return {"purpose": module_doc}

        except Exception as e:
            print(f"Error extracting documentation from {file_path}: {e}")
            return {"purpose": "Error extracting documentation"}

