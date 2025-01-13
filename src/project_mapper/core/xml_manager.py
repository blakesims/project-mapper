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
        
    def _load_template(self, template_path: Path) -> ET.Element:
        """Load and parse XML template.
        
        Args:
            template_path: Path to template file
            
        Returns:
            Parsed XML element tree
            
        Raises:
            FileNotFoundError: If template file not found
            ET.ParseError: If template XML is invalid
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        try:
            tree = ET.parse(template_path)
            root = tree.getroot()
            
            # Check for template extension
            extends = root.get('extends')
            if extends:
                base_path = template_path.parent / extends
                base_root = self._load_template(base_path)
                merged_root = self._merge_templates(base_root, root)
                return merged_root
                
            return root
        except ET.ParseError as e:
            logging.error(f"Invalid XML in template {template_path}: {e}")
            raise
            
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
        
    def update_project_map(self, structure: Dict):
        """Update project map in .cursorrules file.
        
        Args:
            structure: Project structure dictionary
        """
        # Load template(s)
        template_root = self._load_templates([])  # For now, just load base template
        
        # If .cursorrules exists, preserve existing content
        if self.cursorrules_path.exists():
            try:
                tree = ET.parse(self.cursorrules_path)
                existing_root = tree.getroot()
                
                # Merge template with existing, preserving project-map
                merged_root = self._merge_templates(template_root, existing_root)
                template_root = merged_root
            except ET.ParseError as e:
                logging.warning(f"Error parsing existing .cursorrules, creating new: {e}")
        
        # Update project-map section
        project_map = template_root.find("project-map")
        if project_map is None:
            project_map = ET.SubElement(template_root, "project-map")
            
        # Clear existing structure
        structure_elem = project_map.find("structure")
        if structure_elem is not None:
            project_map.remove(structure_elem)
            
        # Add new structure
        structure_elem = ET.SubElement(project_map, "structure")
        self._add_structure(structure_elem, structure)
        
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