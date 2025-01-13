"""Core functionality for scanning project structure and managing docstrings."""

from pathlib import Path
import ast
from typing import Dict, Optional
import logging
from .cursorrules_manager import CursorRulesManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectScanner:
    """Core scanner for project structure and documentation."""
    
    def __init__(self, project_root: Path):
        """Initialize the project scanner.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.rules_manager = CursorRulesManager(project_root)
    
    def scan_project(self) -> Dict:
        """Scan project and return structure with docstrings.
        
        Returns:
            Dict containing the project structure with docstrings
        """
        logger.info(f"Scanning project at {self.project_root}")
        return self._scan_directory(self.src_path)
    
    def _scan_directory(self, path: Path) -> Dict:
        """Recursively scan directory for Python files.
        
        Args:
            path: Directory path to scan
            
        Returns:
            Dict containing directory structure and docstrings
        """
        structure = {}
        try:
            for item in path.iterdir():
                if item.name.startswith('__'):
                    continue
                if item.is_dir():
                    sub_structure = self._scan_directory(item)
                    if sub_structure:  # Only include non-empty directories
                        structure[str(item.relative_to(self.project_root))] = sub_structure
                elif item.suffix == '.py':
                    docstring = self._get_docstring(item)
                    if docstring:  # Only include files with docstrings
                        structure[str(item.relative_to(self.project_root))] = docstring
        except Exception as e:
            logger.error(f"Error scanning directory {path}: {e}")
        return structure
    
    def _get_docstring(self, file_path: Path) -> Optional[str]:
        """Extract module docstring from Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Docstring if found, None otherwise
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())
            return ast.get_docstring(tree)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def update_cursorrules(self, structure: Dict):
        """Update .cursorrules XML file with current project structure.
        
        Args:
            structure: Project structure dict from scan_project()
        """
        self.rules_manager.update_project_map(structure) 