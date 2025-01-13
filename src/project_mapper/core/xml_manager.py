"""XML management for project documentation."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional

class XMLManager:
    """Manages project documentation in XML format."""
    
    def __init__(self, project_root: Path, template_dir: Optional[Path] = None):
        """Initialize XML manager.
        
        Args:
            project_root: Project root directory
            template_dir: Optional directory containing templates
        """
        self.project_root = Path(project_root)
        self.rules_path = project_root / ".cursorrules"
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
    
    def ensure_rules_file(self, language: str = "base"):
        """Create or validate rules file.
        
        Args:
            language: Language-specific template to use
        """
        if not self.rules_path.exists():
            self._create_initial_rules(language)
    
    def _create_initial_rules(self, language: str):
        """Create initial XML structure from template.
        
        Args:
            language: Language-specific template to use
        """
        # Load base template
        base_template = self._load_template("base")
        if base_template is None:
            base_template = self._create_base_structure()
        
        # Load language-specific template if different from base
        if language != "base":
            lang_template = self._load_template(language)
            if lang_template is not None:
                self._merge_templates(base_template, lang_template)
        
        self._write_xml(base_template)
    
    def _load_template(self, name: str) -> Optional[ET.Element]:
        """Load template from file.
        
        Args:
            name: Template name (e.g., 'base', 'python')
            
        Returns:
            Root element of template or None if not found
        """
        template_path = self.template_dir / f"{name}.xml"
        try:
            tree = ET.parse(template_path)
            return tree.getroot()
        except Exception as e:
            print(f"Could not load template {name}: {e}")
            return None
    
    def _create_base_structure(self) -> ET.Element:
        """Create minimal base XML structure.
        
        Returns:
            Root element with basic structure
        """
        root = ET.Element("project-rules")
        
        # Add code rules section
        rules = ET.SubElement(root, "code-rules")
        docstrings = ET.SubElement(rules, "docstrings")
        template = ET.SubElement(docstrings, "template")
        template.text = "Document purpose and relationships"
        
        # Add project map section
        project_map = ET.SubElement(root, "project-map")
        structure = ET.SubElement(project_map, "structure")
        relationships = ET.SubElement(project_map, "relationships")
        
        return root
    
    def _merge_templates(self, base: ET.Element, language: ET.Element):
        """Merge language-specific template into base template.
        
        Args:
            base: Base template root element
            language: Language-specific template root element
        """
        # Simple merge strategy: replace sections if they exist
        for section in language:
            existing = base.find(section.tag)
            if existing is not None:
                base.remove(existing)
            base.append(section)
    
    def update_project_map(self, structure: Dict):
        """Update project map while preserving other sections.
        
        Args:
            structure: Project structure and documentation
        """
        try:
            if not self.rules_path.exists():
                self.ensure_rules_file()
            
            tree = ET.parse(self.rules_path)
            root = tree.getroot()
            
            # Update project-map section
            project_map = root.find("project-map")
            if project_map is None:
                project_map = ET.SubElement(root, "project-map")
            
            # Clear existing structure
            project_map.clear()
            
            # Add new structure
            structure_elem = ET.SubElement(project_map, "structure")
            self._add_structure(structure_elem, structure)
            
            # Add relationships
            relationships = ET.SubElement(project_map, "relationships")
            self._add_relationships(relationships, structure)
            
            self._write_xml(root)
            
        except Exception as e:
            print(f"Error updating project map: {e}")
            self.ensure_rules_file()
            self.update_project_map(structure)
    
    def _add_structure(self, parent: ET.Element, structure: Dict):
        """Add structure to XML recursively.
        
        Args:
            parent: Parent XML element
            structure: Structure dictionary
        """
        for key, value in structure.items():
            if isinstance(value, dict):
                if 'purpose' in value:  # File entry
                    file_elem = ET.SubElement(parent, "file")
                    file_elem.set("name", key)
                    
                    purpose = ET.SubElement(file_elem, "purpose")
                    purpose.text = value.get('purpose', '')
                    
                    if 'components' in value:
                        components = ET.SubElement(file_elem, "components")
                        for comp in value['components']:
                            component = ET.SubElement(components, "component")
                            component.set("type", comp.get('type', ''))
                            component.set("name", comp.get('name', ''))
                            component.text = comp.get('description', '')
                else:  # Directory
                    dir_elem = ET.SubElement(parent, "directory")
                    dir_elem.set("name", key)
                    self._add_structure(dir_elem, value)
    
    def _add_relationships(self, parent: ET.Element, structure: Dict):
        """Add relationships section to XML.
        
        Args:
            parent: Parent XML element
            structure: Structure dictionary
        """
        flow = ET.SubElement(parent, "flow")
        flow.set("description", "Project documentation flow")
        flow.text = "Documentation maintained by LLM based on code analysis"
    
    def _write_xml(self, root: ET.Element):
        """Write formatted XML to file.
        
        Args:
            root: Root element to write
        """
        try:
            ET.indent(root, space="  ")
            tree = ET.ElementTree(root)
            tree.write(self.rules_path, encoding="utf-8", xml_declaration=True)
        except Exception as e:
            print(f"Error writing XML file: {e}") 