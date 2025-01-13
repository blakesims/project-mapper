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
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Optional, List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_REPO = "https://github.com/blakesims/project-mapper-templates.git"
TEMPLATE_README_URL = "https://github.com/blakesims/project-mapper-templates#creating-your-own"

class TemplateManager:
    """Manages template submodule setup and selection."""
    
    def __init__(self, project_root: Path):
        """Initialize template manager.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.project_mapper_dir = self.project_root / ".project-mapper"
        self.template_dir = self.project_mapper_dir / "templates"
        self.config_file = self.project_mapper_dir / "config.json"
        self._load_config()
        
    def check_template_updates(self) -> Dict[str, List[str]]:
        """Check for available template updates.
        
        Returns:
            Dictionary containing:
            - 'modified': List of files that will be modified
            - 'added': List of files that will be added
            - 'deleted': List of files that will be deleted
            - 'error': List of error messages if any
        """
        result = {
            'modified': [],
            'added': [],
            'deleted': [],
            'error': []
        }
        
        if not self.project_mapper_dir.exists():
            result['error'].append("Templates not initialized. Run --setup-templates first.")
            return result
            
        try:
            # Fetch latest changes without applying them
            subprocess.run(
                ["git", "fetch", "origin", "main"],
                cwd=self.project_mapper_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Get status of changes between current HEAD and origin/main
            diff = subprocess.run(
                ["git", "diff", "--name-status", "HEAD..origin/main"],
                cwd=self.project_mapper_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Parse the diff output
            for line in diff.stdout.splitlines():
                if not line.strip():
                    continue
                    
                status, *files = line.split()
                file_path = files[0]
                
                if not file_path.startswith('templates/'):
                    continue
                    
                if status == 'M':
                    result['modified'].append(file_path)
                elif status == 'A':
                    result['added'].append(file_path)
                elif status == 'D':
                    result['deleted'].append(file_path)
                elif status == 'R':
                    # Handle renamed files
                    old_path, new_path = files
                    if old_path.startswith('templates/'):
                        result['deleted'].append(old_path)
                    if new_path.startswith('templates/'):
                        result['added'].append(new_path)
            
            # Check for uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_mapper_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            if status.stdout.strip():
                result['error'].append(
                    "Warning: You have uncommitted changes in your templates. "
                    "These will be lost if you update."
                )
            
        except subprocess.CalledProcessError as e:
            result['error'].append(f"Error checking for updates: {e}")
            
        return result
        
    def update_templates(self) -> bool:
        """Update templates to latest version.
        
        Returns:
            True if update was successful
        """
        try:
            # Reset any local changes
            subprocess.run(
                ["git", "reset", "--hard", "HEAD"],
                cwd=self.project_mapper_dir,
                check=True
            )
            
            # Pull latest changes
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.project_mapper_dir,
                check=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error updating templates: {e}")
            return False
        
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
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Loaded template config: {self.config}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                
    def _save_config(self):
        """Save template configuration."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Saved template config: {self.config}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        return (self.project_root / ".git").exists()
        
    def _setup_submodule(self, repo_url: str) -> bool:
        """Setup template submodule.
        
        Args:
            repo_url: Template repository URL
            
        Returns:
            True if setup successful
        """
        try:
            subprocess.run(
                ["git", "submodule", "add", repo_url, ".project-mapper"],
                cwd=self.project_root,
                check=True
            )
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=self.project_root,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up submodule: {e}")
            return False
        
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
        # First, check if we need to setup the template repository
        if not self.template_dir.exists():
            if not self._is_git_repo():
                print("Not a git repository. Please initialize git first.")
                return None, None
                
            print("\nProject-specific templates not found.")
            choice = input("Do you have a template repository? (yes/no): ").lower()
            
            if choice == 'yes':
                print(f"\nPlease see {TEMPLATE_README_URL}")
                repo_url = input("Enter your template repository URL: ")
            else:
                print("\nUsing default template repository...")
                repo_url = DEFAULT_TEMPLATE_REPO
            
            if not self._setup_submodule(repo_url):
                return None, None
        
        # Now list and select templates
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
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Getting template paths for base={base_name}, extension={extension_name}")
        
        if base_name:
            base_path = self.template_dir / f"{base_name}.xml"
            if base_path.exists():
                paths.append(base_path)
                
        if extension_name:
            ext_path = self.template_dir / f"{extension_name}.xml"
            if ext_path.exists():
                paths.append(ext_path)
                
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Found template paths: {paths}")
        return paths 
