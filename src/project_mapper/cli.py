"""Command line interface for project-mapper.

Key Components:
    main(): CLI entry point handling template setup and project scanning

Project Dependencies:
    This file uses: 
        - TemplateManager: For template setup and selection
        - XMLManager: For documentation updates
        - PythonScanner: For Python file scanning
"""

import argparse
from pathlib import Path

from .adapters.python import PythonScanner
from .core.xml_manager import XMLManager
from .git.hooks import GitHookManager
from .template_manager import TemplateManager

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
        "--template", "-t",
        type=str,
        help="Template name to use (will prompt if not specified)"
    )
    parser.add_argument(
        "--install-hooks",
        action="store_true",
        help="Install git hooks"
    )
    parser.add_argument(
        "--setup-templates",
        action="store_true",
        help="Setup or change template repository"
    )
    
    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    
    # Handle template setup
    template_manager = TemplateManager(project_root)
    template_name = None
    
    if args.setup_templates:
        template_name = template_manager.setup_templates()
        if template_name:
            print(f"\nTemplate set to: {template_name}")
            print("You can change templates anytime with: project-mapper --setup-templates")
        return
    
    # Get template path
    if args.template:
        template_name = args.template
    elif not template_manager.template_dir.exists():
        print("\nNo project-specific templates found.")
        setup = input("Would you like to set them up now? (yes/no): ").lower()
        if setup == 'yes':
            template_name = template_manager.setup_templates()
    
    template_path = template_manager.get_template_path(template_name) if template_name else None
    
    # Install git hooks if requested
    if args.install_hooks:
        try:
            hook_manager = GitHookManager(project_root, template_path)
            hook_manager.install_hooks()
            return
        except Exception as e:
            print(f"Error installing hooks: {e}")
            return
    
    # Initialize components
    xml_manager = XMLManager(project_root, template_path)
    
    # Create scanner based on language
    if args.language == "python":
        scanner = PythonScanner(project_root)
    else:
        raise ValueError(f"Unsupported language: {args.language}")
    
    # Scan project and update documentation
    print(f"\nScanning {project_root}...")
    structure = scanner.scan_project()
    
    print("Updating documentation...")
    xml_manager.update_project_map(structure)
    print("Done!")
    
    if template_name:
        print(f"\nUsing template: {template_name}")
        print("You can change templates anytime with: project-mapper --setup-templates")

if __name__ == "__main__":
    main() 