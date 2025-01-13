"""Core scanning functionality for project documentation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

class BaseScanner(ABC):
    """Abstract base class for language-specific scanners."""
    
    def __init__(self, project_root: Path):
        """Initialize scanner with project root.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
    
    @abstractmethod
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file should be processed.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file should be processed, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_documentation(self, file_path: Path) -> Dict:
        """Extract documentation from source file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Dictionary containing extracted documentation:
            {
                'purpose': str,
                'components': List[Dict],
                'dependencies': Dict[str, List[str]]
            }
        """
        pass
    
    def detect_dependencies(self, file_path: Path) -> List[str]:
        """Optional dependency detection.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            List of detected dependencies
        """
        return []
    
    def scan_project(self) -> Dict:
        """Scan project directory for supported files.
        
        Returns:
            Dictionary containing project structure and documentation
        """
        return self._scan_directory(self.project_root)
    
    def _scan_directory(self, path: Path) -> Dict:
        """Recursively scan directory.
        
        Args:
            path: Directory to scan
            
        Returns:
            Dictionary containing directory structure and documentation
        """
        structure = {}
        try:
            for item in path.iterdir():
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    sub_structure = self._scan_directory(item)
                    if sub_structure:  # Only include non-empty directories
                        structure[str(item.relative_to(self.project_root))] = sub_structure
                        
                elif self.is_supported_file(item):
                    try:
                        docs = self.extract_documentation(item)
                        if docs:  # Only include files with documentation
                            structure[str(item.relative_to(self.project_root))] = docs
                    except Exception as e:
                        # Log but continue processing other files
                        print(f"Error processing {item}: {e}")
        
        except Exception as e:
            print(f"Error scanning directory {path}: {e}")
        
        return structure 