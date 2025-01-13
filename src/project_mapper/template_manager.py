"""Template management for project-mapper.

Key Components:
    TemplateManager: Handles template submodule setup and selection
    setup_templates(): Guides user through template setup process

Project Dependencies:
    This file uses: git: For submodule operations
    This file is used by: CLI: For template initialization
"""

import subprocess
from pathlib import Path
from typing import Optional, List

DEFAULT_TEMPLATE_REPO = "https://github.com/yourusername/project-mapper-templates.git"
TEMPLATE_README_URL = "https://github.com/yourusername/project-mapper-templates#creating-your-own"

class TemplateManager:
    """Manages template submodule setup and selection."""
    
    def __init__(self, project_root: Path):
        """Initialize template manager.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.template_dir = self.project_root / ".project-mapper"
    
    def setup_templates(self) -> Optional[str]:
        """Guide user through template setup process.
        
        Returns:
            Selected template name or None if setup failed
        """
        if not self._is_git_repo():
            print("Not a git repository. Please initialize git first.")
            return None
            
        if self.template_dir.exists():
            return self._select_template()
            
        print("\nProject-specific templates not found.")
        choice = input("Do you have a template repository? (yes/no): ").lower()
        
        if choice == 'yes':
            print(f"\nPlease see {TEMPLATE_README_URL}")
            repo_url = input("Enter your template repository URL: ")
        else:
            print("\nUsing default template repository...")
            repo_url = DEFAULT_TEMPLATE_REPO
        
        if self._setup_submodule(repo_url):
            return self._select_template()
        return None
    
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
            print(f"Error setting up submodule: {e}")
            return False
    
    def _select_template(self) -> Optional[str]:
        """Let user select a template.
        
        Returns:
            Selected template name or None if no templates found
        """
        templates = self._find_templates()
        if not templates:
            print("No templates found.")
            return None
            
        print("\nAvailable templates:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template}")
        
        try:
            choice = int(input("\nSelect template number (or 0 for default): "))
            if choice == 0:
                return "base"
            return templates[choice - 1].stem
        except (ValueError, IndexError):
            print("Invalid selection. Using default template.")
            return "base"
    
    def _find_templates(self) -> List[Path]:
        """Find available templates.
        
        Returns:
            List of template file paths
        """
        if not self.template_dir.exists():
            return []
            
        templates_dir = self.template_dir / "templates"
        if not templates_dir.exists():
            return []
            
        return list(templates_dir.glob("*.xml"))
    
    def get_template_path(self, name: str) -> Optional[Path]:
        """Get path to selected template.
        
        Args:
            name: Template name
            
        Returns:
            Path to template or None if not found
        """
        if name == "base":
            return None
            
        template_path = self.template_dir / "templates" / f"{name}.xml"
        return template_path if template_path.exists() else None 