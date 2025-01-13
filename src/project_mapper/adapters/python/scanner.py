"""Python-specific implementation of project scanner."""

import ast
from pathlib import Path
from typing import Dict, List, Optional

from ...core.scanner import BaseScanner

class PythonScanner(BaseScanner):
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
            - purpose: Module docstring
            - components: List of class/function info
            - dependencies: Import relationships
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())
            
            # Get module docstring
            module_doc = ast.get_docstring(tree) or "No description available"
            
            # Extract components (classes/functions)
            components = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    if not node.name.startswith('_'):  # Skip private members
                        doc = ast.get_docstring(node) or "No description"
                        components.append({
                            'name': node.name,
                            'type': 'class' if isinstance(node, ast.ClassDef) else 'function',
                            'description': doc.split('\n')[0]
                        })
            
            # Get dependencies
            dependencies = self.detect_dependencies(file_path)
            
            return {
                'purpose': module_doc.split('\n')[0],
                'components': components,
                'dependencies': dependencies
            }
            
        except Exception as e:
            print(f"Error extracting documentation from {file_path}: {e}")
            return {}
    
    def detect_dependencies(self, file_path: Path) -> List[str]:
        """Detect Python file dependencies through imports.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of dependency descriptions
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())
            
            dependencies = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if not name.name.startswith('_'):
                            dependencies.append(f"{name.name}: Module import")
                elif isinstance(node, ast.ImportFrom):
                    if not node.module.startswith('_'):
                        module = node.module or ""
                        for name in node.names:
                            if not name.name.startswith('_'):
                                dependencies.append(f"{module}.{name.name}: Specific import")
            
            return dependencies
            
        except Exception as e:
            print(f"Error detecting dependencies in {file_path}: {e}")
            return [] 