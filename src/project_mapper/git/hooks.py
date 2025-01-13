"""Git hook management for project-mapper."""

import os
import shutil
from pathlib import Path
from typing import Optional

class GitHookManager:
    """Manages git hooks for project-mapper."""
    
    def __init__(self, project_root: Path, template_dir: Optional[Path] = None):
        """Initialize hook manager.
        
        Args:
            project_root: Project root directory
            template_dir: Optional directory containing hook templates
        """
        self.project_root = Path(project_root)
        self.git_dir = self.project_root / ".git"
        self.hooks_dir = self.git_dir / "hooks"
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates" / "hooks"
    
    def install_hooks(self):
        """Install git hooks from templates."""
        if not self.git_dir.exists():
            raise ValueError(f"Not a git repository: {self.project_root}")
        
        # Create hooks directory if it doesn't exist
        self.hooks_dir.mkdir(exist_ok=True)
        
        # Install pre-commit hook
        self._install_hook("pre-commit")
    
    def _install_hook(self, hook_name: str):
        """Install a specific git hook.
        
        Args:
            hook_name: Name of the hook to install
        """
        src = self.template_dir / hook_name
        dst = self.hooks_dir / hook_name
        
        if not src.exists():
            raise ValueError(f"Hook template not found: {hook_name}")
        
        # Copy hook file
        shutil.copy2(src, dst)
        
        # Make executable
        os.chmod(dst, 0o755)
        
        print(f"Installed {hook_name} hook") 