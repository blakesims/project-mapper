"""Command line interface for project-mapper."""

import argparse
from pathlib import Path

from .adapters.python import PythonScanner
from .core.xml_manager import XMLManager
from .git.hooks import GitHookManager

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Project documentation mapper")
    parser.add_argument(
        "--project-root", "-p",
        type=str,
        default=".",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        default="python",
        choices=["python"],
        help="Project language (default: python)"
    )
    parser.add_argument(
        "--template-dir", "-t",
        type=str,
        help="Custom template directory"
    )
    parser.add_argument(
        "--install-hooks",
        action="store_true",
        help="Install git hooks"
    )
    
    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    template_dir = Path(args.template_dir) if args.template_dir else None
    
    # Install git hooks if requested
    if args.install_hooks:
        try:
            hook_manager = GitHookManager(project_root, template_dir)
            hook_manager.install_hooks()
            return
        except Exception as e:
            print(f"Error installing hooks: {e}")
            return
    
    # Initialize components
    xml_manager = XMLManager(project_root, template_dir)
    
    # Create scanner based on language
    if args.language == "python":
        scanner = PythonScanner(project_root)
    else:
        raise ValueError(f"Unsupported language: {args.language}")
    
    # Scan project and update documentation
    print(f"Scanning {project_root}...")
    structure = scanner.scan_project()
    
    print("Updating documentation...")
    xml_manager.update_project_map(structure)
    print("Done!")

if __name__ == "__main__":
    main() 