"""XML management for project documentation.

Key Components:
    XMLManager: Handles reading, writing, and merging of XML templates and .cursorrules
    _merge_templates(): Merges multiple XML templates while respecting inheritance
    _load_template(): Loads and validates XML templates

Project Dependencies:
    This file uses: 
        - ElementTree: For XML parsing and manipulation
        - Path: For file path handling
    This file is used by: CLI: For template management and documentation updates
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, List
import logging

class XMLManager:
    """Manages XML templates and .cursorrules file."""
    
    def __init__(self, project_root: Path, template_dir: Optional[Path] = None):
        """Initialize XML manager.
        
        Args:
            project_root: Project root directory
            template_dir: Optional custom template directory
        """
        self.project_root = Path(project_root)
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        self.cursorrules_path = self.project_root / ".cursorrules"
        
    def _load_template(self, template_path: Optional[Path] = None) -> ET.Element:
        """Load XML template from file."""
        if template_path is None:
            template_path = self.template_dir / "base.xml"
        
        try:
            tree = ET.parse(template_path)
            return tree.getroot()
        except (ET.ParseError, FileNotFoundError) as e:
            logging.error(f"Failed to load template {template_path}: {e}")
            # Create empty root element
            return ET.Element("project-rules")
        
    def _merge_templates(self, base: ET.Element, extension: ET.Element) -> ET.Element:
        """Merge extension template into base template.
        
        Args:
            base: Base template XML element
            extension: Extension template XML element
            
        Returns:
            Merged XML element
        """
        # Create a deep copy of base to avoid modifying original
        merged = ET.fromstring(ET.tostring(base))
        
        # Helper function for recursive merging
        def merge_element(target: ET.Element, source: ET.Element):
            # Merge attributes
            target.attrib.update(source.attrib)
            
            # Create lookup of existing child elements by tag
            existing = {child.tag: child for child in target}
            
            for child in source:
                if child.tag in existing:
                    # If element exists in base, recursively merge
                    merge_element(existing[child.tag], child)
                else:
                    # If new element, append to base
                    target.append(ET.fromstring(ET.tostring(child)))
        
        # Start merge from root
        merge_element(merged, extension)
        return merged
        
    def _load_templates(self, template_paths: List[Path]) -> ET.Element:
        """Load and merge multiple templates.
        
        Args:
            template_paths: List of template paths to load
            
        Returns:
            Merged template XML element
        """
        if not template_paths:
            # Load default base template
            base_path = self.template_dir / "base.xml"
            return self._load_template(base_path)
            
        # Load and merge all templates
        base = self._load_template(template_paths[0])
        for path in template_paths[1:]:
            extension = self._load_template(path)
            base = self._merge_templates(base, extension)
            
        return base
        
    def indent(self, elem: ET.Element, level: int = 0) -> None:
        """Add proper indentation to element tree."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                self.indent(subelem, level + 1)
                if not subelem.tail or not subelem.tail.strip():
                    subelem.tail = i
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
            if elem.text:
                # Handle text content
                text = elem.text.strip()
                if "\n" in text:
                    # Multi-line text - preserve newlines but add indentation
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    elem.text = i + "  " + ("\n" + i + "  ").join(lines)
                else:
                    # Single line text - wrap at 80 chars
                    words = text.split()
                    lines = []
                    current_line = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) + 1 <= 80:
                            current_line.append(word)
                            current_length += len(word) + 1
                        else:
                            if current_line:
                                lines.append(" ".join(current_line))
                            current_line = [word]
                            current_length = len(word)
                    
                    if current_line:
                        lines.append(" ".join(current_line))
                    
                    if len(lines) > 1:
                        elem.text = i + "  " + ("\n" + i + "  ").join(lines)
                    else:
                        elem.text = i + "  " + text

    def update_project_map(self, structure: Dict) -> None:
        """Update project map in .cursorrules file."""
        # Load base template
        template_root = self._load_template()
        
        # Get or create project-map section
        project_map = template_root.find("project-map")
        if project_map is None:
            project_map = ET.SubElement(template_root, "project-map")
        
        # Clear and update structure
        structure_elem = project_map.find("structure")
        if structure_elem is None:
            structure_elem = ET.SubElement(project_map, "structure")
        else:
            structure_elem.clear()
        
        # Add new structure
        self._add_structure(structure_elem, structure)
        
        # Add proper indentation
        self.indent(template_root)
        
        # Write updated XML
        tree = ET.ElementTree(template_root)
        tree.write(self.cursorrules_path, encoding="utf-8", xml_declaration=True)
        
    def _add_structure(self, parent: ET.Element, structure: Dict):
        """Recursively add structure to XML element.
        
        Args:
            parent: Parent XML element
            structure: Structure dictionary
        """
        for name, value in structure.items():
            if isinstance(value, dict):
                if 'purpose' in value:  # File entry
                    file_elem = ET.SubElement(parent, "file")
                    file_elem.set("name", name)
                    
                    # Add purpose from docstring
                    purpose = ET.SubElement(file_elem, "purpose")
                    purpose.text = value['purpose']
                    
                    # Add components if present
                    if value.get('components'):
                        components = ET.SubElement(file_elem, "components")
                        for comp in value['components']:
                            comp_elem = ET.SubElement(components, "component")
                            comp_elem.set("type", comp['type'])
                            comp_elem.set("name", comp['name'])
                            comp_elem.text = comp['description']
                else:  # Directory
                    dir_elem = ET.SubElement(parent, "directory")
                    dir_elem.set("name", name)
                    self._add_structure(dir_elem, value) 