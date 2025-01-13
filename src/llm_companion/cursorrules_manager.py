"""Manages .cursorrules file creation and updates, maintaining XML structure and project documentation."""

import xml.etree.ElementTree as ET
from pathlib import Path
import logging
import ast
from typing import List, Optional

logger = logging.getLogger(__name__)

class CursorRulesManager:
    """Manages .cursorrules file updates and maintains documentation standards."""
    
    def __init__(self, project_root: Path):
        """Initialize the cursor rules manager.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.rules_path = project_root / ".cursorrules"
        self.template_dir = Path(__file__).parent / "templates"
        self.ensure_rules_file()
    
    def ensure_rules_file(self):
        """Create .cursorrules if it doesn't exist."""
        if not self.rules_path.exists():
            logger.info("Creating initial .cursorrules file")
            self._create_initial_rules()
    
    def _create_initial_rules(self):
        """Create initial XML structure with docstring policy and LLM guidelines."""
        root = ET.Element("project-rules")
        
        # Add LLM guidelines from template
        guidelines = self._load_guidelines_template()
        if guidelines is not None:
            root.append(guidelines)
        
        # Add project map section
        project_map = ET.SubElement(root, "project-map")
        structure = ET.SubElement(project_map, "structure")
        relationships = ET.SubElement(project_map, "relationships")
        
        self._write_xml(root)
    
    def _load_guidelines_template(self) -> Optional[ET.Element]:
        """Load LLM guidelines from template file.
        
        Returns:
            Guidelines XML element or None if template not found
        """
        template_path = self.template_dir / "llm_guidelines.xml"
        try:
            tree = ET.parse(template_path)
            return tree.getroot()
        except Exception as e:
            logger.warning(f"Could not load guidelines template: {e}")
            return None
    
    def update_project_map(self, structure: dict):
        """Update project-map section in .cursorrules while preserving guidelines.
        
        Args:
            structure: Dictionary containing project structure and docstrings
        """
        try:
            tree = ET.parse(self.rules_path)
            root = tree.getroot()
            
            # Preserve guidelines
            guidelines = root.find("llm-guidelines")
            
            # Update guidelines if template has changed
            new_guidelines = self._load_guidelines_template()
            if new_guidelines is not None:
                if guidelines is not None:
                    root.remove(guidelines)
                root.append(new_guidelines)
            
            # Clear and recreate project-map
            project_map = root.find("project-map")
            if project_map is not None:
                root.remove(project_map)
            project_map = ET.SubElement(root, "project-map")
            
            # Add new structure
            structure_elem = ET.SubElement(project_map, "structure")
            file_paths = self._add_structure(structure_elem, structure)
            
            # Add relationships section with enhanced flow
            relationships = ET.SubElement(project_map, "relationships")
            self._add_relationships(relationships)
            
            # Write back to file
            self._write_xml(root)
            logger.info("Updated project map in .cursorrules")
            
        except ET.ParseError as e:
            logger.warning(f"Invalid .cursorrules XML, creating new: {e}")
            self._create_initial_rules()
            self.update_project_map(structure)
        except Exception as e:
            logger.error(f"Error updating project map: {e}")
    
    def _add_structure(self, parent: ET.Element, structure: dict, current_path="") -> List[Path]:
        """Recursively add structure to XML with enhanced documentation.
        
        Args:
            parent: Parent XML element to add structure to
            structure: Dictionary containing structure information
            current_path: Current path in the directory structure
            
        Returns:
            List of processed file paths
        """
        processed_files = []
        for key, value in structure.items():
            path = key.replace("📁 ", "").replace("📄 ", "")
            parts = path.split("/")
            name = parts[-1]
            
            if isinstance(value, dict):
                dir_elem = ET.SubElement(parent, "directory")
                dir_elem.set("name", name)
                processed_files.extend(
                    self._add_structure(dir_elem, value, f"{current_path}/{name}" if current_path else name)
                )
            else:
                file_path = self.project_root / path
                file_elem = ET.SubElement(parent, "file")
                file_elem.set("name", name)
                
                # Add detailed purpose
                purpose = ET.SubElement(file_elem, "purpose")
                purpose.text = value.split('\n')[0] if value else "No description available"
                
                # Add key components with enhanced descriptions
                key_components = ET.SubElement(file_elem, "key_components")
                self._add_key_components(key_components, file_path)
                
                # Add dependencies (to be maintained by LLM)
                dependencies = ET.SubElement(file_elem, "dependencies")
                self._add_core_dependencies(dependencies, name)
                
                processed_files.append(file_path)
        
        return processed_files
    
    def _add_core_dependencies(self, parent: ET.Element, filename: str):
        """Add core project dependencies (maintained by LLM).
        
        Args:
            parent: Parent XML element to add dependencies to
            filename: Name of the file to add dependencies for
        """
        outgoing = ET.SubElement(parent, "outgoing")
        
        if filename == "core.py":
            dep = ET.SubElement(outgoing, "dependency")
            dep.text = "CursorRulesManager: For maintaining XML documentation"
        elif filename == "cursorrules_manager.py":
            dep = ET.SubElement(outgoing, "dependency")
            dep.text = "ProjectScanner: For project structure analysis"
    
    def _add_key_components(self, parent: ET.Element, file_path: Path):
        """Extract and add key components (classes/functions) from a Python file.
        
        Args:
            parent: Parent XML element to add components to
            file_path: Path to the Python file
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    if not node.name.startswith('_'):  # Skip private members
                        component = ET.SubElement(parent, "component")
                        docstring = ast.get_docstring(node) or "No description"
                        description = docstring.split('\n')[0] if docstring else "No description"
                        if isinstance(node, ast.ClassDef):
                            component.text = f"{node.name}: {description}"
                        else:
                            component.text = f"{node.name}(): {description}"
        except Exception as e:
            logger.warning(f"Could not analyze components in {file_path}: {e}")
    
    def _add_relationships(self, parent: ET.Element):
        """Add detailed relationships between components.
        
        Args:
            parent: Parent XML element to add relationships to
        """
        flow = ET.SubElement(parent, "flow")
        flow.set("description", "Project documentation process")
        flow.text = (
            "ProjectScanner analyzes project structure and docstrings → "
            "CursorRulesManager maintains XML documentation"
        )
    
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