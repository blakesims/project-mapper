"""Abstract base adapter interface for language-specific scanners."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

class BaseAdapter(ABC):
    """Abstract base class for language-specific scanners."""
    
    def __init__(self, project_root: Path):
        """Initialize scanner.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
    
    @abstractmethod
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file should be processed.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file should be processed
        """
        pass
    
    @abstractmethod
    def extract_documentation(self, file_path: Path) -> Dict:
        """Extract documentation from source file.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Dictionary containing:
                - purpose: File's purpose
                - components: List of components (classes/functions)
        """
        pass
    
    def scan_project(self) -> Dict:
        """Scan project directory for supported files.
        
        Returns:
            Dictionary of file paths to documentation
        """
        structure = {}
        
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue
                
            if not self.is_supported_file(file_path):
                continue
                
            rel_path = file_path.relative_to(self.project_root)
            parent = structure
            
            # Build directory structure
            for part in rel_path.parent.parts:
                if part not in parent:
                    parent[part] = {}
                parent = parent[part]
            
            # Add file documentation
            try:
                parent[rel_path.name] = self.extract_documentation(file_path)
            except Exception as e:
                print(f"Error processing {rel_path}: {e}")
                continue
        
        return structure 