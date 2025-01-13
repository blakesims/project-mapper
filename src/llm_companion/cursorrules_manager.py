"""Manages .cursorrules file creation and updates, maintaining XML structure and project documentation."""

import xml.etree.ElementTree as ET
from pathlib import Path
import logging
import ast
from typing import Dict, Set, List

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
        self.ensure_rules_file()
    
    def ensure_rules_file(self):
        """Create .cursorrules if it doesn't exist."""
        if not self.rules_path.exists():
            logger.info("Creating initial .cursorrules file")
            self._create_initial_rules()
    
    def _create_initial_rules(self):
        """Create initial XML structure with docstring policy."""
        root = ET.Element("project-rules")
        
        # Add docstring policy
        rules = ET.SubElement(root, "rules")
        docstring_policy = ET.SubElement(rules, "docstring-policy")
        
        requirement = ET.SubElement(docstring_policy, "requirement")
        requirement.text = "All Python files must maintain up-to-date docstrings"
        
        format_elem = ET.SubElement(docstring_policy, "format")
        purpose = ET.SubElement(format_elem, "purpose")
        purpose.text = "Clear statement of file's responsibility"
        key_components = ET.SubElement(format_elem, "key_components")
        key_components.text = "List main classes/functions"
        dependencies = ET.SubElement(format_elem, "dependencies")
        dependencies.text = "Document relationships"
        
        update_trigger = ET.SubElement(docstring_policy, "update-trigger")
        update_trigger.text = "Any functional changes to file"
        
        # Add project map section
        project_map = ET.SubElement(root, "project-map")
        structure = ET.SubElement(project_map, "structure")
        relationships = ET.SubElement(project_map, "relationships")
        
        self._write_xml(root)
    
    def update_project_map(self, structure: dict):
        """Update project-map section in .cursorrules.
        
        Args:
            structure: Dictionary containing project structure and docstrings
        """
        try:
            tree = ET.parse(self.rules_path)
            root = tree.getroot()
            
            # Preserve rules section
            rules = root.find("rules")
            
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
            self._add_relationships(relationships, file_paths)
            
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
                
                # Add dependencies
                dependencies = ET.SubElement(file_elem, "dependencies")
                deps = self._analyze_dependencies(file_path)
                
                outgoing = ET.SubElement(dependencies, "outgoing")
                for dep in sorted(deps["outgoing"]):
                    dep_elem = ET.SubElement(outgoing, "dependency")
                    dep_elem.text = dep
                
                incoming = ET.SubElement(dependencies, "incoming")
                processed_files.append(file_path)
        
        return processed_files
    
    def _analyze_dependencies(self, file_path: Path) -> Dict[str, Set[str]]:
        """Analyze file dependencies through import statements.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with outgoing and incoming dependencies
        """
        dependencies = {"outgoing": set(), "incoming": set()}
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        dependencies["outgoing"].add(f"{name.name}: Module import")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        dependencies["outgoing"].add(f"{module}.{name.name}: Specific import")
        except Exception as e:
            logger.warning(f"Could not analyze dependencies in {file_path}: {e}")
        
        return dependencies
    
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
    
    def _add_relationships(self, parent: ET.Element, file_paths: List[Path]):
        """Add detailed relationships between components.
        
        Args:
            parent: Parent XML element to add relationships to
            file_paths: List of processed file paths
        """
        flow = ET.SubElement(parent, "flow")
        flow.set("description", "Project documentation process")
        flow.text = (
            "ProjectScanner analyzes project structure and docstrings → "
            "CursorRulesManager maintains XML documentation"
        )
        
        # Add file relationships based on imports
        for file_path in file_paths:
            if file_path.name == "core.py":
                relationship = ET.SubElement(parent, "relationship")
                relationship.set("type", "core-functionality")
                relationship.text = (
                    "core.ProjectScanner provides scanning functionality → "
                    "cursorrules_manager.CursorRulesManager uses it for updates"
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