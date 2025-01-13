"""Manages .cursorrules file creation and updates."""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)

class CursorRulesManager:
    """Manages .cursorrules file updates."""
    
    def __init__(self, project_root: Path):
        """Initialize the cursor rules manager.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.rules_path = project_root / ".cursorrules"
        self.ensure_rules_file()
    
    def ensure_rules_file(self):
        """Create .cursorrules if it doesn't exist."""
        if not self.rules_path.exists():
            logger.info("Creating initial .cursorrules file")
            self._create_initial_rules()
    
    def _create_initial_rules(self):
        """Create initial XML structure."""
        root = ET.Element("project-rules")
        project_map = ET.SubElement(root, "project-map")
        project_map.set("timestamp", datetime.now(timezone.utc).isoformat())
        project_map.set("git-commit", self._get_git_commit())
        structure = ET.SubElement(project_map, "structure")
        self._write_xml(root)
    
    def update_project_map(self, structure: dict):
        """Update project-map section in .cursorrules.
        
        Args:
            structure: Dictionary containing project structure and docstrings
        """
        try:
            tree = ET.parse(self.rules_path)
            root = tree.getroot()
            
            # Find or create project-map section
            project_map = root.find("project-map")
            if project_map is None:
                project_map = ET.SubElement(root, "project-map")
            
            # Clear existing structure
            project_map.clear()
            
            # Update timestamp and git info
            project_map.set("timestamp", datetime.now(timezone.utc).isoformat())
            project_map.set("git-commit", self._get_git_commit())
            
            # Add new structure
            structure_elem = ET.SubElement(project_map, "structure")
            self._add_structure(structure_elem, structure)
            
            # Write back to file
            self._write_xml(root)
            logger.info("Updated project map in .cursorrules")
            
        except ET.ParseError as e:
            logger.warning(f"Invalid .cursorrules XML, creating new: {e}")
            self._create_initial_rules()
            self.update_project_map(structure)
        except Exception as e:
            logger.error(f"Error updating project map: {e}")
    
    def _add_structure(self, parent: ET.Element, structure: dict):
        """Recursively add structure to XML.
        
        Args:
            parent: Parent XML element to add structure to
            structure: Dictionary containing structure information
        """
        for key, value in structure.items():
            if isinstance(value, dict):
                dir_elem = ET.SubElement(parent, "directory")
                dir_elem.set("name", key.replace("📁 ", ""))
                self._add_structure(dir_elem, value)
            else:
                file_elem = ET.SubElement(parent, "file")
                file_elem.set("name", key.replace("📄 ", ""))
                docstring = ET.SubElement(file_elem, "docstring")
                docstring.text = value
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash.
        
        Returns:
            Current git commit hash or 'unknown' if not in a git repository
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Failed to get git commit: {e}")
        return "unknown"
    
    def _write_xml(self, root: ET.Element):
        """Write formatted XML to file.
        
        Args:
            root: Root XML element to write
        """
        try:
            ET.indent(root, space="  ")  # Requires Python 3.9+
            tree = ET.ElementTree(root)
            tree.write(self.rules_path, encoding="utf-8", xml_declaration=True)
        except Exception as e:
            logger.error(f"Error writing XML file: {e}") 