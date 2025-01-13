"""Python-specific implementation of project scanner."""

import ast
from pathlib import Path
from typing import Dict, List, Optional

from ..base import BaseAdapter

class PythonScanner(BaseAdapter):
    """Scanner implementation for Python projects."""
    
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file is a Python source file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is a .py file and not a special file
        """
        return (
            file_path.suffix == '.py' and
            not file_path.name.startswith('__')
        )
    
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
            
            return {
                'purpose': module_doc
            }
            
        except Exception as e:
            print(f"Error extracting documentation from {file_path}: {e}")
            return {
                'purpose': "Error extracting documentation"
            } 