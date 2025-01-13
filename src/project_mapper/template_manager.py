"""Template management for project-mapper.

Key Components:
    TemplateManager: Handles template submodule setup and selection
    setup_templates(): Guides user through template setup process

Project Dependencies:
    This file uses: git: For submodule operations
    This file is used by: CLI: For template initialization
"""

import os
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages template submodule setup and selection."""
    
    def __init__(self, project_root: Path):
        """Initialize template manager.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.template_dir = self.project_root / ".project-mapper" / "templates"
        self.config_file = self.project_root / ".project-mapper" / "config.json"
        self._load_config()
        
    def _load_config(self):
        """Load template configuration."""
        self.config = {
            'base_template': None,
            'extension_template': None
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    self.config.update(json.load(f))
                logger.debug(f"Loaded template config: {self.config}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                
    def _save_config(self):
        """Save template configuration."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.debug(f"Saved template config: {self.config}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
        
    def list_available_templates(self) -> List[Path]:
        """List available XML templates in template directory.
        
        Returns:
            List of paths to XML template files
        """
        if not self.template_dir.exists():
            return []
            
        return list(self.template_dir.glob("*.xml"))
        
    def get_template_info(self, template_path: Path) -> Tuple[str, Optional[str]]:
        """Get template name and its base template if it extends one.
        
        Args:
            template_path: Path to template file
            
        Returns:
            Tuple of (template name, base template name if extends one)
        """
        try:
            tree = ET.parse(template_path)
            root = tree.getroot()
            extends = root.get('extends')
            return (template_path.stem, extends)
        except Exception as e:
            logger.error(f"Error reading template {template_path}: {e}")
            return (template_path.stem, None)
        
    def setup_templates(self) -> Tuple[str, Optional[str]]:
        """Guide user through template setup process.
        
        Returns:
            Tuple of (selected base template name, selected extension template name)
        """
        templates = self.list_available_templates()
        if not templates:
            print("No templates found in .project-mapper/templates/")
            return None, None
            
        # First, identify base templates and extensions
        base_templates = []
        extension_templates = []
        
        for template in templates:
            name, extends = self.get_template_info(template)
            if extends is None:
                base_templates.append(template)
            else:
                extension_templates.append((template, extends))
        
        # Select base template
        print("\nAvailable base templates:")
        for i, template in enumerate(base_templates, 1):
            print(f"{i}. {template.stem}")
        
        while True:
            try:
                choice = int(input("\nSelect base template (number): ")) - 1
                if 0 <= choice < len(base_templates):
                    base_template = base_templates[choice]
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Find available extensions for selected base
        available_extensions = [
            ext for ext, base in extension_templates 
            if base == f"{base_template.stem}.xml"
        ]
        
        extension_template = None
        if available_extensions:
            print("\nAvailable extensions:")
            print("0. None (skip)")
            for i, ext in enumerate(available_extensions, 1):
                print(f"{i}. {ext.stem}")
            
            while True:
                try:
                    choice = int(input("\nSelect extension (0 for none): ")) - 1
                    if choice == -1:
                        break
                    if 0 <= choice < len(available_extensions):
                        extension_template = available_extensions[choice]
                        break
                    print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a number.")
        
        # Save selections
        self.config['base_template'] = base_template.stem
        self.config['extension_template'] = extension_template.stem if extension_template else None
        self._save_config()
        
        return base_template.stem, extension_template.stem if extension_template else None
        
    def get_template_paths(self, base_name: Optional[str] = None, extension_name: Optional[str] = None) -> List[Path]:
        """Get paths for selected templates.
        
        Args:
            base_name: Name of base template (if None, use from config)
            extension_name: Name of extension template (if None, use from config)
            
        Returns:
            List of template paths to use
        """
        paths = []
        
        # Use config values if not specified
        base_name = base_name or self.config.get('base_template')
        extension_name = extension_name or self.config.get('extension_template')
        
        logger.debug(f"Getting template paths for base={base_name}, extension={extension_name}")
        
        if base_name:
            base_path = self.template_dir / f"{base_name}.xml"
            if base_path.exists():
                paths.append(base_path)
                
        if extension_name:
            ext_path = self.template_dir / f"{extension_name}.xml"
            if ext_path.exists():
                paths.append(ext_path)
                
        logger.debug(f"Found template paths: {paths}")
        return paths 
